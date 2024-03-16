//! # Words
//!
//! Determine if a word is a valid entry in a game and how it's entered
//!
//! ## Word Trajectory
//!
//! A `WordTrajectory` represents a trajectory of indices that form
//! a word in the game.
//!
//! ## Word Trajectories
//!
//! `WordTrajectories` is an iterator that yields possible word trajectories
//! given a word and available letters.
//!
//! ## Example
//!
//! ```rust
//! use  letter_boxed::solver::words::{can_make_word, WordTrajectory};
//!
//! fn main() {
//!     let word = "map";
//!     let letters = "uigaangbpiam";
//!
//!     let trajectories = can_make_word(word, letters);
//!     for traj in trajectories {
//!         println!("{:?}", traj);
//!     }
//! }
//! ```
//!

use ::rand::Rng;
use std::collections::{HashMap, VecDeque};

/// Represents a trajectory of word formation.
#[derive(Debug, Clone)]
pub struct WordTrajectory {
    indices: Vec<usize>,
}

impl WordTrajectory {
    /// Creates a new empty `WordTrajectory`.
    pub fn new() -> WordTrajectory {
        WordTrajectory {
            indices: Vec::new(),
        }
    }

    /// Adds an index to the trajectory.
    ///
    /// # Arguments
    ///
    /// * `i` - The index to be added.
    ///
    /// # Returns
    ///
    /// A new `WordTrajectory` with the added index.
    pub fn add_index(&self, i: usize) -> WordTrajectory {
        let mut next_vec = self.indices.clone();
        next_vec.push(i);
        WordTrajectory { indices: next_vec }
    }

    /// Returns the number of indices in the trajectory.
    pub fn len(&self) -> usize {
        self.indices.len()
    }

    /// Returns the last index in the trajectory, if available.
    pub fn last(&self) -> Option<usize> {
        if self.len() == 0 {
            return None;
        }
        Some(*self.indices.last().unwrap())
    }

    /// Returns a reference to the vector of indices in the trajectory.
    pub fn indices(&self) -> &Vec<usize> {
        &self.indices
    }
}

type LetterIndices = HashMap<char, Vec<usize>>;

/// An iterator over possible trajectories through letters
/// to form a given word
#[derive(Debug)]
pub struct WordTrajectories<'a> {
    word: &'a str,
    letters: LetterIndices,
    s: usize,
    queue: VecDeque<WordTrajectory>,
}

impl<'a> WordTrajectories<'a> {
    /// Create a new collection of trajectories
    pub fn new(word: &'a str, letters: &'a str) -> WordTrajectories<'a> {
        return WordTrajectories {
            word: word,
            letters: Self::_letter_indices(letters),
            s: letters.len() / 4,
            queue: VecDeque::from([WordTrajectory::new()]),
        };
    }

    /// BFS visit behavior
    pub fn _visit(
        word: &str,
        letters: &LetterIndices,
        s: usize,
        queue: &mut VecDeque<WordTrajectory>,
    ) -> Option<WordTrajectory> {
        // First, pop the latest Trajectory to search
        if let Some(trajectory) = queue.pop_front() {
            // Success condition: no letters left
            if word.len() == trajectory.len() {
                return Some(trajectory);
            }

            // Otherwise: create new trajectories to check
            // by iteratively appending possible valid
            // next steps

            // Dissect the word into the first char and the suffix slice
            let cur_char_idx = trajectory.len();
            let c0 = word.chars().nth(cur_char_idx)?;
            // If the letter isn't in the game, immediately fail
            if !letters.contains_key(&c0) {
                return None;
            }

            // Iterate over the possible next indices
            let next_locs = letters.get(&c0)?;

            for next_loc in next_locs {
                // If we have a trajectory, check if the next
                // letter can be placed
                if let Some(cur_loc) = trajectory.last() {
                    if cur_loc / s == next_loc / s {
                        continue;
                    }
                }
                // Otherwise, queue up the extended trajectories
                // (Preferentially push these to the front of the
                // queue so we search deeper before broader)
                queue.push_front(trajectory.add_index(*next_loc));
            }
        }
        return None;
    }

    /// Preprocess: Convert letters into a collection that maps letters
    /// to their occurrence indices in the game board
    fn _letter_indices(letters: &str) -> LetterIndices {
        let mut hash_letters: LetterIndices = HashMap::new();
        for (i, l) in letters.chars().enumerate() {
            let occurrences = hash_letters.get_mut(&l);

            match occurrences {
                Some(indices) => {
                    indices.push(i);
                    indices.sort()
                }
                None => {
                    hash_letters.insert(l, vec![i]);
                }
            }
        }
        return hash_letters;
    }
}

impl<'a> Iterator for WordTrajectories<'a> {
    type Item = WordTrajectory;

    fn next(&mut self) -> Option<Self::Item> {
        while !self.queue.is_empty() {
            // Iterate until we get a valid word, then
            // immediately return - state maintained by the queue
            if let Some(success) = Self::_visit(self.word, &self.letters, self.s, &mut self.queue) {
                return Some(success);
            }
        }
        return None;
    }
}

/// Generates a random string of the specified length composed of lowercase English letters.
///
/// # Arguments
///
/// * `length` - The length of the random string to generate.
///
/// # Returns
///
/// A randomly generated string of the specified length.
pub fn random_string(length: usize) -> String {
    const CHARSET: &[u8] = b"abcdefghijklmnopqrstuvwxyz";

    let mut rng = rand::thread_rng();
    let random_string: String = (0..length)
        .map(|_| {
            let index = rng.gen_range(0..CHARSET.len());
            CHARSET[index] as char
        })
        .collect();

    random_string
}

/// Determines if a word can be formed using the given letters.
///
/// This function returns a `WordTrajectories` iterator that yields possible trajectories
/// for forming the word using the provided letters.
///
/// # Arguments
///
/// * `word` - The word to form trajectories for.
/// * `letters` - The available letters to form the word.
///
/// # Returns
///
/// An iterator yielding possible trajectories for forming the word.
pub fn can_make_word<'a>(word: &'a str, letters: &'a str) -> WordTrajectories<'a> {
    WordTrajectories::new(word, letters)
}

#[cfg(test)]
mod tests {

    use super::{can_make_word, random_string, WordTrajectories, WordTrajectory};
    use std::iter::zip;

    #[test]
    fn word_trajectories() {
        // Empty trajectory
        let traj = WordTrajectory::new();
        assert_eq!(traj.last(), None);

        // Add an index
        let traj2 = traj.add_index(0);
        assert_eq!(traj2.last(), Some(0));
        assert_eq!(traj2.len(), 1);
    }

    #[test]
    fn s3_can_make_word() {
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

        let letters = "uigaangbpiam";

        // This is a valid word
        let word = "map";
        let trajectories = can_make_word(word, letters);
        let keys = [[11, 4, 8], [11, 3, 8]];
        for (traj, key) in zip(trajectories, keys) {
            assert_eq!(*traj.indices(), key);
        }

        // Another valid word
        let word = "magi";
        let trajectories = can_make_word(word, letters);
        let keys = [
            [11, 4, 6, 9],
            [11, 4, 6, 1],
            [11, 4, 2, 9],
            [11, 3, 6, 9],
            [11, 3, 6, 1],
            [11, 3, 2, 9],
        ];
        for (traj, key) in zip(trajectories, keys) {
            assert_eq!(*traj.indices(), key);
        }

        let word = "paan";
        let trajectories = can_make_word(word, letters);
        let keys = [[8, 4, 10, 5], [8, 3, 10, 5]];
        for (traj, key) in zip(trajectories, keys) {
            assert_eq!(*traj.indices(), key);
        }

        let word = "panini";
        let trajectories = can_make_word(word, letters);
        let keys = [
            [8, 10, 5, 9, 5, 9],
            [8, 10, 5, 9, 5, 1],
            [8, 10, 5, 1, 5, 9],
            [8, 10, 5, 1, 5, 1],
        ];
        for (traj, key) in zip(trajectories, keys) {
            assert_eq!(*traj.indices(), key);
        }

        let word = "gaining";
        let trajectories = can_make_word(word, letters);
        let mut keys = [
            [2, 3, 1, 5, 1, 5, 2],
            [2, 3, 1, 5, 1, 5, 6],
            [2, 3, 1, 5, 9, 5, 2],
            [2, 3, 1, 5, 9, 5, 6],
            [2, 3, 9, 5, 1, 5, 2],
            [2, 3, 9, 5, 1, 5, 6],
            [2, 3, 9, 5, 9, 5, 2],
            [2, 3, 9, 5, 9, 5, 6],
            [2, 4, 1, 5, 1, 5, 2],
            [2, 4, 1, 5, 1, 5, 6],
            [2, 4, 1, 5, 9, 5, 2],
            [2, 4, 1, 5, 9, 5, 6],
            [2, 4, 9, 5, 1, 5, 2],
            [2, 4, 9, 5, 1, 5, 6],
            [2, 4, 9, 5, 9, 5, 2],
            [2, 4, 9, 5, 9, 5, 6],
            [2, 10, 1, 5, 1, 5, 2],
            [2, 10, 1, 5, 1, 5, 6],
            [2, 10, 1, 5, 9, 5, 2],
            [2, 10, 1, 5, 9, 5, 6],
            [6, 3, 1, 5, 1, 5, 2],
            [6, 3, 1, 5, 1, 5, 6],
            [6, 3, 1, 5, 9, 5, 2],
            [6, 3, 1, 5, 9, 5, 6],
            [6, 3, 9, 5, 1, 5, 2],
            [6, 3, 9, 5, 1, 5, 6],
            [6, 3, 9, 5, 9, 5, 2],
            [6, 3, 9, 5, 9, 5, 6],
            [6, 4, 1, 5, 1, 5, 2],
            [6, 4, 1, 5, 1, 5, 6],
            [6, 4, 1, 5, 9, 5, 2],
            [6, 4, 1, 5, 9, 5, 6],
            [6, 4, 9, 5, 1, 5, 2],
            [6, 4, 9, 5, 1, 5, 6],
            [6, 4, 9, 5, 9, 5, 2],
            [6, 4, 9, 5, 9, 5, 6],
            [6, 10, 1, 5, 1, 5, 2],
            [6, 10, 1, 5, 1, 5, 6],
            [6, 10, 1, 5, 9, 5, 2],
            [6, 10, 1, 5, 9, 5, 6],
        ];
        keys.reverse();
        for (traj, key) in zip(trajectories, keys) {
            assert_eq!(*traj.indices(), key);
        }

        // These are invalid words
        let word = "maam";
        let mut trajectories = can_make_word(word, letters);
        assert!(trajectories.next().is_none());
        let word = "asdfs";
        let mut trajectories = can_make_word(word, letters);
        assert!(trajectories.next().is_none());
    }

    #[test]
    fn s2_can_make_word() {
        /*
        -------------
          U G
        M     A
        I     N
          P G
        -------------
        */
        let letters = "ugangpim";

        let word = "magi";
        let trajectories = can_make_word(word, letters);
        let keys = [[7, 2, 4, 6], [7, 2, 1, 6]];
        for (traj, key) in zip(trajectories, keys) {
            assert_eq!(*traj.indices(), key);
        }

        let word = "pig";
        let trajectories = can_make_word(word, letters);
        let keys = [[5, 6, 4], [5, 6, 1]];
        for (traj, key) in zip(trajectories, keys) {
            assert_eq!(*traj.indices(), key);
        }

        let word = "gum";
        let trajectories = can_make_word(word, letters);
        let keys = [[4, 0, 7]];
        for (traj, key) in zip(trajectories, keys) {
            assert_eq!(*traj.indices(), key);
        }
    }

    #[test]
    fn huge_can_make_word() {
        let s = 10;
        let letters = &random_string(s * 4);
        println!("{}", letters);
        let word = "map";
        let trajectories = can_make_word(word, letters);
        for traj in trajectories {
            // println!("{:?}", traj);
        }
    }
}
