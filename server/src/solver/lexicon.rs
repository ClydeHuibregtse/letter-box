use serde::Deserialize;
use std::fs::File;
use std::io::Read;
use std::error::Error;
use serde_json::from_str;

pub const LEXICON_PATH: &str = "/Users/clyde/Documents/letter_box_project/letter-box/server/src/solver/lexicon.json";

#[derive(Debug, Deserialize)]
pub struct Lexicon {
    data: Vec<Vec<String>>,
}

impl Lexicon {

    pub fn new(file_path: &str) -> Result<Lexicon, Box<dyn Error>> {
        // Read from lexicon checked into this repo
        let mut file = File::open(file_path)?;
        let mut contents = String::new();
        file.read_to_string(&mut contents)?;
        let my_data: Lexicon = from_str(&contents)?;

        Ok(my_data)
    }

    pub fn words_starting_with(&self, l: char) -> &Vec<String> {
        // ord('a') = 97
        let index = l as usize - 97;
        &self.data[index]
    }
}



#[cfg(test)]
mod tests {

    use super::{Lexicon, LEXICON_PATH};

    #[test]
    fn english_words() {
        let words = Lexicon::new(LEXICON_PATH).unwrap();
        words.words_starting_with('a');
    }
}