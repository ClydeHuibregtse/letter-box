//! # Lexicon
//!
//! The `Lexicon` module provides functionality for working with a lexicon of words.
//!
//! ## Usage
//!
//! ```rust
//! use  letter_boxed::solver::lexicon::{Lexicon, LEXICON_PATH};
//!
//! fn main() {
//!     let words = Lexicon::new(LEXICON_PATH).unwrap();
//!     let words_starting_with_a = words.words_starting_with('a');
//!     println!("{:?}", words_starting_with_a);
//! }
//! ```
//!
//! ## Example
//!
//! ```rust
//! use  letter_boxed::solver::lexicon::{Lexicon, LEXICON_PATH};
//!
//! fn main() {
//!     let words = Lexicon::new(LEXICON_PATH).unwrap();
//!     let words_starting_with_a = words.words_starting_with('a');
//!     println!("{:?}", words_starting_with_a);
//! }
//! ```
//!
//! ## Structure
//!
//! - `Lexicon`: Represents a lexicon of words.
//! - `LEXICON_PATH`: Path to the lexicon JSON file.
//!
//! ## Methods
//!
//! - `new(file_path: &str) -> Result<Lexicon, Box<dyn Error>>`: Constructs a new `Lexicon` instance by reading data from a JSON file specified by `file_path`.
//! - `words_starting_with(&self, l: char) -> &Vec<String>`: Returns a reference to a vector containing words starting with the specified character `l`.
//!
//! ## Dependencies
//!
//! - `serde`: For serializing and deserializing JSON data.
//!
//! ## Notes
//!
//! - The lexicon JSON file should have the structure `{"data": [["word1", "word2", ...], ["word3", "word4", ...], ...]}`.
//!
//! ## Example
//!
//! ```rust
//! use letter_boxed::solver::lexicon::{Lexicon, LEXICON_PATH};
//!
//! #[test]
//! fn english_words() {
//!     let words = Lexicon::new(LEXICON_PATH).unwrap();
//!     let words_starting_with_a = words.words_starting_with('a');
//! }
//! ```
//!

use serde::Deserialize;
use serde_json::from_str;
use std::error::Error;
use std::fs::File;
use std::io::Read;

/// Path to the lexicon JSON file.
pub const LEXICON_PATH: &str = "./lexicon.json";

/// Represents a lexicon of words.
#[derive(Debug, Deserialize)]
pub struct Lexicon {
    data: Vec<Vec<String>>,
}

impl Lexicon {
    /// Constructs a new `Lexicon` instance by reading data from a JSON file specified by `file_path`.
    pub fn new(file_path: &str) -> Result<Lexicon, Box<dyn Error>> {
        let full_path = format!("{}/{}", std::env::var("DATA_DIR").unwrap(), file_path);
        println!("{}", full_path);
        let mut file = File::open(full_path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        let my_data: Lexicon = from_str(&contents)?;

        Ok(my_data)
    }

    /// Returns a reference to a vector containing words starting with the specified character `l`.
    pub fn words_starting_with(&self, l: char) -> &Vec<String> {
        let index = l as usize - 97;
        &self.data[index]
    }

    /// Return a vector of all words
    pub fn all(&self) -> Vec<String> {
        self.data.iter().flat_map(|v| v.iter().cloned()).collect()
    }
}

#[cfg(test)]
mod tests {
    use super::{Lexicon, LEXICON_PATH};

    #[test]
    fn english_words() {
        let words = Lexicon::new(LEXICON_PATH).unwrap();
        let words_starting_with_a = words.words_starting_with('a');
        assert!(!words_starting_with_a.is_empty());
    }
}
