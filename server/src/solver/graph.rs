// GraphNodes

use std::{cmp::Ordering, collections::{BinaryHeap, HashMap, HashSet}};
use num::{range, BigUint, FromPrimitive, One};
use super::{lexicon::{Lexicon, LEXICON_PATH}, words::{can_make_word, WordTrajectory}};


#[derive(Debug, Hash, PartialEq, Eq, Clone)]
pub struct NodeID(usize, BigUint);


#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Node {
    id: NodeID
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct Edge <'a> {
    prev: NodeID,
    next: NodeID,
    word: &'a str    
}


#[derive(Debug, Clone)]
pub struct Graph <'a> {
    nodes: Vec<Node>,
    edges: Vec<Edge<'a>>,
    node_indices: HashMap<NodeID, usize>,
}

impl Node {

    pub fn new(index: usize, state: BigUint) -> Node {
        Node { id: NodeID(index, state)}
    }
    pub fn state(&self) -> &BigUint {
        &self.id.1
    }
    
    pub fn index(&self) -> usize {
        self.id.0
    }
    
    pub fn transition(&self, traj: WordTrajectory) -> Node {
        // Generate the GraphNode that appears when w is inserted into the game
        let mut new_state = self.state().clone();
        for index in traj.indices() {
            new_state |= BigUint::one() << index;
        }
        return Node::new(*traj.indices().last().unwrap(), new_state.clone())
    }

    pub fn score(&self) -> usize {
        self.state().count_ones() as usize
    }

}

impl Ord for Node {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        let s = self.score();
        let o = other.score();
        // If we have yet to try a Node with only one letter,
        // we should artificially move this to the surface of the priority queue
        if s == 1 {
            return Ordering::Greater;
        }
        if o == 1 {
            return Ordering::Less; 
        }
        return s.cmp(&o);
    }
}

impl PartialOrd for Node {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}


impl <'a> Graph <'a> {

    pub fn new() -> Graph<'a> {
        return Graph {
            nodes: Vec::new(),
            edges: Vec::new(),
            node_indices: HashMap::new(),
        }
    }

    pub fn nodes(&self) -> &Vec<Node> {
        &self.nodes
    }
    pub fn edges(&self) -> &Vec<Edge> {
        &self.edges
    }

    pub fn from_letters(letters: &str) -> Graph<'a> {
        let mut nodes: Vec<Node> = vec![];
        let mut node_indices: HashMap<NodeID, usize> = HashMap::new();
        let n = letters.len();
        for (i, l) in letters.chars().enumerate() {
            let mut digits = vec![0; n];
            digits[i] = 1;
            let node = Node::new(i, BigUint::new(digits));
            node_indices.insert(node.id.clone(), nodes.len());
            nodes.push(node);
        }
        return Graph {
            nodes: nodes.into_iter().collect(),
            edges: Vec::new(),
            node_indices: node_indices
        }
    }

    pub fn get_node(&self, id: &NodeID) -> Option<&Node> {
        let index = *self.node_indices.get(id)?;
        return self.nodes.get(index);
    }

    pub fn get_edge(&self, id1: &NodeID, id2: &NodeID) -> Option<&Edge> {
        for edge in self.edges() {
            if edge.prev == *id1 && edge.next == *id2 {
                return Some(edge)
            }
        }
        return None
    }
    
    pub fn contains(&self, id: &NodeID) -> bool {
        self.get_node(&id).is_some()
    }

    pub fn add_node(&mut self, id: &NodeID) {
        if !self.node_indices.contains_key(id) {
            let node = Node { id: id.clone() };
            self.node_indices.insert(id.clone(), self.nodes.len());
            self.nodes.push(node);
        }
    }

    fn add_edge(&mut self, prev_id: &NodeID, next_id: &NodeID, word: &'a str) {

        // If nodes not found, add them
        // add_node does nothing if one of these exists
        self.add_node(prev_id);
        self.add_node(next_id);

        let edge = Edge {
            prev: prev_id.clone(),
            next: next_id.clone(),
            word: word
        };
        self.edges.push(edge);
    }

    pub fn generate_edges_for_node(
        &mut self, id: &NodeID, letters: &str, lexicon: &'a Lexicon
    ) -> Option<Vec<Node>>{

        // Get the current letter
        // TODO: fix this unwrap
        let node = self.get_node(&id).unwrap().clone();
        let index = node.index();
        let cur_char = letters.chars().nth(index).unwrap();

        // Get reference to all possible words
        // TODO: prune these even farther given letters that don't appear ?
        let possible_words = lexicon.words_starting_with(cur_char);

        let n_len = self.nodes().len();

        // Iterate over words and construct edges given that word
        for word in possible_words {
            let possible_trajectories = can_make_word(word, letters);
            for trajectory in possible_trajectories {
                let new_node = node.transition(trajectory);
                if new_node.score() > node.score() {
                    self.add_node(&new_node.id);
                    self.add_edge(&node.id, &new_node.id, word);
                    break
                }
            }
        }
        let new_nodes = self.nodes()[n_len..].to_vec();

        return Some(new_nodes)
    }

    fn get_node_path(&mut self, letters: &str, lexicon: &'a Lexicon) -> Option<Vec<NodeID>> {

        let max_score = letters.len();

        // Initialize our priority queue with whatever
        // nodes are currently in the graph
        let mut queue: BinaryHeap<Node> = BinaryHeap::new();
        let binding = self.clone();
        for node in binding.nodes() {
            queue.push(node.clone());
        }

        // Initialize visited hash
        let mut visited: HashSet<NodeID> = HashSet::new();

        // Initialize parent backtrace hash
        let mut parents: HashMap<NodeID, NodeID> = HashMap::new();

        // Start the BFS
        while let Some(node) = queue.pop() {

            // If we've visited this node, we can assume we've already found a faster path
            if visited.contains(&node.id) {
                continue
            }
            visited.insert(node.id.clone());

            println!("Evaluating node: {:?} with score {:?}", &node, &node.score());
            // TODO: fix this unwrap
            let new_nodes = self.generate_edges_for_node(&node.id, letters, lexicon).unwrap();

            // Insert the new nodes
            new_nodes.iter().for_each(|n| {
                parents.insert(n.id.clone(), node.id.clone());
                queue.push(n.clone())
            });
            // println!("{:?}", queue);

            if node.score() == max_score {
                let mut parent = &node.id;
                let mut parents_vec = vec![parent.clone()];
                while let Some(p) = parents.get(&parent) {
                    parents_vec.push(p.clone());
                    parent = &p;
                }
                parents_vec.reverse();
                return Some(parents_vec);
            }
        }
        return None;
    }

    pub fn solve(&mut self, letters: &str, lexicon: &'a Lexicon) -> Option<Vec<&str>> {
        let node_ids = self.get_node_path(letters, lexicon)?;
        let mut words = vec![];
        for i in range(0, node_ids.len() - 1) {
            words.push(self.get_edge(&node_ids[i], &node_ids[i + 1])?.word);
        }
        Some(words)
    }


}


#[cfg(test)]
mod tests {
    use std::{collections::{BinaryHeap, HashSet}, ops::Index};

    use num::{BigUint, FromPrimitive, One, Zero};
    use crate::solver::{graph::NodeID, lexicon::{Lexicon, LEXICON_PATH}, words::random_string};

    use super::{Graph, Node, Edge};

    #[test]
    fn graph_basics() {

        let zero = BigUint::new(vec![0]);
        let one = BigUint::one();

        let n0 = NodeID(0, zero);
        let n1 = NodeID(1, one);

        // Initialize the graph
        let mut g = Graph::new();
    
        // It should be empty
        assert_eq!(g.nodes.len(), 0);

        // Insert a few nodes
        g.add_node(&n0);
        g.add_node(&n1);

        assert_eq!(g.nodes().len(), 2);

        // Start fresh
        let mut g = Graph::new();

        // Add an edge from n0 to n1
        g.add_edge(&n0, &n1, "a");
        assert_eq!(g.edges().len(), 1);

        // Can we find nodes via index/state?
        let found_n0 = g.get_node(&n0).unwrap();
        let found_n1 = g.get_node(&n1).unwrap();
        assert_eq!(&found_n0.id, &n0);
        assert_eq!(&found_n1.id, &n1);

        assert!(g.contains(&n0));
        assert!(g.contains(&n1));
    }

    fn get_set_bit_indices(n: BigUint) -> Vec<usize> {
        let mut indices = Vec::new();
        let mut mask = BigUint::one();
    
        for i in 0..32 {
            if n.clone() & mask.clone() != BigUint::zero() {
                indices.push(i);
            }
            mask <<= 1;
        }
    
        indices
    }

    #[test]
    fn graph_edge_creation() {

        /*
        Here is an example game
        --------------------------------
          U I G
        M       A
        A       A
        I       N
          P B G
        --------------------------------
        */
        // Let's assume we're starting at index 0
        // and constructing all transitions beginning
        // at that node.
        let one = BigUint::one();
        let n0 = NodeID(0, one);
        // Initialize the graph
        let mut g = Graph::new();

        // Insert a node starting at the first letter
        g.add_node(&n0);


        let letters = "uigaangbpiam";
        let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
        g.generate_edges_for_node(&n0, letters, &lexicon);
        // Let's make sure the NodeIDs are correct
        for edge in g.edges() {
            let next_node = g.get_node(&edge.next).unwrap();
            
            // The state of the new game should cover all the letters used in the word
            let indices = get_set_bit_indices(next_node.state().clone());
            let covered_letters: HashSet<char> = indices.iter().map(|i| {letters.chars().nth(*i).unwrap()}).collect();
            let word_letters: HashSet<char> = edge.word.chars().collect();
            assert_eq!(covered_letters, word_letters);

            // The new index should be the last character in the word
            assert_eq!(letters.chars().nth(next_node.index()), edge.word.chars().last())
        }

    }

    #[test]
    fn node_ordering() {

        // The ordering here should be: n0 -> n1 -> n2 -> n3
        let n0 = Node {id: NodeID(0, BigUint::from_usize(2).unwrap())};
        let n1 = Node {id: NodeID(0, BigUint::from_usize(4).unwrap())};
        let n2 = Node {id: NodeID(0, BigUint::from_usize(7).unwrap())};
        let n3 = Node {id: NodeID(0, BigUint::from_usize(3).unwrap())};
        
        // Pairwise compare
        assert!(n0 > n1);
        assert!(n0 > n2);
        assert!(n0 > n3);
        
        assert!(n1 > n2);
        assert!(n1 > n3);
        
        assert!(n2 > n3);
        
        // Can we sort?
        let mut nodes = Vec::from([n3.clone(), n1.clone(), n0.clone(), n2.clone()]);
        nodes.sort();
        assert_eq!(nodes, [n3.clone(), n2.clone(), n1.clone(), n0.clone()]);

        let mut queue = BinaryHeap::from(nodes);
        assert_eq!(queue.pop(), Some(n0.clone()));
        assert_eq!(queue.pop(), Some(n1.clone()));
        assert_eq!(queue.pop(), Some(n2.clone()));
        assert_eq!(queue.pop(), Some(n3.clone()));
        assert_eq!(queue.pop(), None);

    }

    #[test]
    fn graph_search() {

        /*
        Here is an example game
        --------------------------------
          U I G
        M       A
        A       A
        I       N
          P B G
        --------------------------------
        */
        // let letters = "uigaangbpiam";
        // let letters = "asoignfhjudlrueusidorptoeuricsbndfhwquitehds";

        // March 10 '24
        // let letters = "ingkphsratec";
        
        // March 12 '24
        // let letters = "rvheaipnwgmo";

        let letters = random_string(100);
        let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
        let mut g = Graph::from_letters(&letters);
        let words = g.solve(&letters, &lexicon);
        println!("{:?}", words);



    }
}