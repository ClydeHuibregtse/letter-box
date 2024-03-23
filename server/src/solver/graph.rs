//! Graph solutions to letter boxed
//!
//! # Example
//!
//! ```
//! // Example usage of the graph module
//! use letter_boxed::solver::graph::Graph;
//! use letter_boxed::solver::lexicon::{Lexicon, LEXICON_PATH};
//!
//! // Define letters for the word game
//! let letters = "exampleletters";
//!
//! // Create a new graph from the letters
//! let mut graph = Graph::from_letters(&letters);

use super::{
    lexicon::Lexicon,
    words::{can_make_word, WordTrajectory},
};
use num::{BigUint, One, Zero};
use serde::ser::{SerializeStruct, SerializeTupleStruct};
use serde::{Serialize, Serializer};
use std::{
    cmp::Ordering,
    collections::{BinaryHeap, HashMap, HashSet},
};

/// Represents a unique identifier for a node in the graph.
#[derive(Debug, Hash, PartialEq, Eq, Clone)]
pub struct NodeID(usize, BigUint);

// Implement Serialize for NodeID to handle big ints
impl Serialize for NodeID {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_tuple_struct("NodeID", 2)?;
        state.serialize_field(&self.0)?;
        state.serialize_field(&format!("{:b}", &self.1))?;
        state.end()
    }
}

/// Represents a node in the graph.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize)]
pub struct Node {
    id: NodeID,
}

/// Represents a directed edge between nodes in the graph.
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize)]
pub struct Edge<'a> {
    prev: NodeID,
    next: NodeID,
    pub word: &'a str,
}

/// Represents a graph structure.
#[derive(Debug, Clone)]
pub struct Graph<'a> {
    nodes: Vec<Node>,
    edges: Vec<Edge<'a>>,
    node_indices: HashMap<NodeID, usize>,
}

impl Node {
    /// Creates a new node with the given index and state.
    pub fn new(index: usize, state: BigUint) -> Node {
        Node {
            id: NodeID(index, state),
        }
    }

    pub fn from_id(node_id: NodeID) -> Node {
        Node { id: node_id }
    }
    /// Returns a reference to the state of the node.
    pub fn state(&self) -> &BigUint {
        &self.id.1
    }

    /// Returns the index of the node.
    pub fn index(&self) -> usize {
        self.id.0
    }

    /// Generates a new node by transitioning from the current node based on the given trajectory.
    pub fn transition(&self, traj: WordTrajectory) -> Node {
        let mut new_state = self.state().clone();
        for index in traj.indices() {
            new_state |= BigUint::one() << index;
        }
        // TODO: double iteration over indices
        Node::new(*traj.indices().last().unwrap(), new_state.clone())
    }

    /// Computes and returns the score of the node.
    pub fn score(&self) -> usize {
        self.state().count_ones() as usize
    }
}

impl Ord for Node {
    fn cmp(&self, other: &Self) -> std::cmp::Ordering {
        let s = self.score();
        let o = other.score();
        if s == 1 {
            return Ordering::Greater;
        }
        if o == 1 {
            return Ordering::Less;
        }
        s.cmp(&o)
    }
}

impl PartialOrd for Node {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}

impl<'a> Graph<'a> {
    /// Creates a new empty graph.
    pub fn new() -> Graph<'a> {
        Graph {
            nodes: Vec::new(),
            edges: Vec::new(),
            node_indices: HashMap::new(),
        }
    }

    /// Returns a reference to the nodes in the graph.
    pub fn nodes(&self) -> &Vec<Node> {
        &self.nodes
    }

    /// Returns a reference to the edges in the graph.
    pub fn edges(&self) -> &Vec<Edge> {
        &self.edges
    }

    /// Creates a graph from the given letters.
    pub fn from_letters(letters: &str) -> Graph<'a> {
        let mut nodes: Vec<Node> = vec![];
        let mut node_indices: HashMap<NodeID, usize> = HashMap::new();
        for (i, _l) in letters.chars().enumerate() {
            let mut state = BigUint::zero();
            state.set_bit(i as u64, true);
            let node = Node::new(i, state);
            node_indices.insert(node.id.clone(), nodes.len());
            nodes.push(node);
        }
        Graph {
            nodes: nodes.into_iter().collect(),
            edges: Vec::new(),
            node_indices: node_indices,
        }
    }

    /// Returns a reference to the node with the given ID, if it exists.
    pub fn get_node(&self, id: &NodeID) -> Option<&Node> {
        let index = *self.node_indices.get(id)?;
        self.nodes.get(index)
    }

    /// Returns a reference to the edge between the nodes with the given IDs, if it exists.
    pub fn get_edge(&self, id1: &NodeID, id2: &NodeID) -> Option<&Edge> {
        for edge in self.edges() {
            if edge.prev == *id1 && edge.next == *id2 {
                return Some(edge);
            }
        }
        None
    }

    /// Checks if the graph contains a node with the given ID.
    pub fn contains(&self, id: &NodeID) -> bool {
        self.get_node(&id).is_some()
    }

    /// Adds a node to the graph if it doesn't already exist.
    pub fn add_node(&mut self, id: &NodeID) {
        if !self.node_indices.contains_key(id) {
            let node = Node { id: id.clone() };
            self.node_indices.insert(id.clone(), self.nodes.len());
            self.nodes.push(node);
        }
    }

    /// Adds an edge to the graph.
    fn add_edge(&mut self, prev_id: &NodeID, next_id: &NodeID, word: &'a str) {
        self.add_node(prev_id);
        self.add_node(next_id);

        let edge = Edge {
            prev: prev_id.clone(),
            next: next_id.clone(),
            word: word,
        };
        self.edges.push(edge);
    }

    /// Generates edges for the given node based on the provided letters and lexicon.
    pub fn generate_edges_for_node(
        &mut self,
        id: &NodeID,
        letters: &str,
        lexicon: &'a Lexicon,
    ) -> Option<Vec<Node>> {
        let node = self.get_node(&id).unwrap().clone();
        let index = node.index();
        let cur_char = letters.chars().nth(index).unwrap();
        let possible_words = lexicon.words_starting_with(cur_char);
        let n_len = self.nodes().len();

        for word in possible_words {
            let possible_trajectories = can_make_word(word, letters);
            for trajectory in possible_trajectories {
                let new_node = node.transition(trajectory);
                if new_node.score() > node.score() {
                    self.add_node(&new_node.id);
                    self.add_edge(&node.id, &new_node.id, word);
                    break;
                }
            }
        }
        let new_nodes = self.nodes()[n_len..].to_vec();
        Some(new_nodes)
    }

    /// Finds the path of nodes with maximum score based on the given letters and lexicon.
    pub fn get_node_path(&mut self, letters: &str, lexicon: &'a Lexicon) -> Option<Vec<NodeID>> {
        let max_score = letters.len();
        println!("{}", max_score);
        let mut queue: BinaryHeap<Node> = BinaryHeap::new();
        let binding = self.clone();
        for node in binding.nodes() {
            queue.push(node.clone());
        }

        let mut visited: HashSet<NodeID> = HashSet::new();
        let mut parents: HashMap<NodeID, NodeID> = HashMap::new();

        while let Some(node) = queue.pop() {
            if visited.contains(&node.id) {
                continue;
            }
            visited.insert(node.id.clone());

            let new_nodes = self
                .generate_edges_for_node(&node.id, letters, lexicon)
                .unwrap();

            new_nodes.iter().for_each(|n| {
                parents.insert(n.id.clone(), node.id.clone());
                queue.push(n.clone())
            });

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
        None
    }
}

// Omit node_indices from the serialization of the graph as it is
// simply an implementation detail
impl<'a> Serialize for Graph<'a> {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        let mut state = serializer.serialize_struct("Graph", 2)?;
        state.serialize_field("nodes", &self.nodes)?;
        state.serialize_field("edges", &self.edges)?;
        state.end()
    }
}

#[cfg(test)]
mod tests {
    use std::collections::{BinaryHeap, HashSet};

    use crate::solver::{
        graph::NodeID,
        lexicon::{Lexicon, LEXICON_PATH},
        words::WordTrajectory,
    };
    use num::{pow::Pow, BigUint, FromPrimitive, One, Zero};
    use serde_json::json;

    use super::{Edge, Graph, Node};

    #[test]
    fn node_basics() {
        // Test basic implementation of Nodes
        // Construct a node
        let node = Node::new(0, BigUint::one());

        // Node setup should be okay
        assert_eq!(*node.state(), BigUint::one());
        assert_eq!(node.index(), 0);

        // Let's try a transition
        // (arbitrary trajectory)
        let mut traj = WordTrajectory::new();
        let indices = vec![0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11];
        indices.iter().for_each(|i| {
            traj = traj.add_index(*i);
        });
        // (transition the node)
        let new_node = node.transition(traj);

        assert_eq!(new_node.index(), 11);
        // (new state should be 2^N - 1)
        assert_eq!(
            *new_node.state(),
            BigUint::from_isize(2.pow(indices.len()) as isize - 1).unwrap()
        );
    }

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
            let covered_letters: HashSet<char> = indices
                .iter()
                .map(|i| letters.chars().nth(*i).unwrap())
                .collect();
            let word_letters: HashSet<char> = edge.word.chars().collect();
            assert_eq!(covered_letters, word_letters);

            // The new index should be the last character in the word
            assert_eq!(
                letters.chars().nth(next_node.index()),
                edge.word.chars().last()
            )
        }
    }

    #[test]
    fn node_ordering() {
        // The ordering here should be: n0 -> n1 -> n2 -> n3
        let n0 = Node {
            id: NodeID(0, BigUint::from_usize(2).unwrap()),
        };
        let n1 = Node {
            id: NodeID(0, BigUint::from_usize(4).unwrap()),
        };
        let n2 = Node {
            id: NodeID(0, BigUint::from_usize(7).unwrap()),
        };
        let n3 = Node {
            id: NodeID(0, BigUint::from_usize(3).unwrap()),
        };

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
    fn test_graph_serialize() {
        // Make simple objects and test their (potentially custom)
        // JSON serialization

        // A Node with a BigUint state
        let n0 = Node {
            id: NodeID(0, BigUint::from_usize(2).unwrap()),
        };
        let node_json = json!(n0);
        assert_eq!(json!({"id":[0,"10"]}), node_json);

        let n1 = Node {
            id: NodeID(0, BigUint::from_usize(256).unwrap()),
        };
        let node_json = json!(n1);
        assert_eq!(json!({"id":[0,"100000000"]}), node_json);

        let n2 = Node {
            id: NodeID(14, BigUint::from_usize(7).unwrap()),
        };
        let node_json = json!(n2);
        assert_eq!(json!({"id":[14,"111"]}), node_json);

        // An Edge
        let e1 = Edge {
            prev: n0.id.clone(),
            next: n2.id.clone(),
            word: "test",
        };
        let edge_json = json!(e1);
        assert_eq!(
            json!({"next":[14,"111"],"prev":[0,"10"],"word":"test"}),
            edge_json
        );

        // A Graph
        // Empty
        let mut g = Graph::new();
        assert_eq!(json!({"nodes": [], "edges": []}), json!(g));

        // Add an edge/node
        g.add_edge(&e1.prev, &e1.next, "test");
        assert_eq!(
            json!({
                "nodes": [json!(n0), json!(n2)],
                "edges": [json!(e1)]
            }),
            json!(g)
        );
    }
}
