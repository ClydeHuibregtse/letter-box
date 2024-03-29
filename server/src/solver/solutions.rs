//! Primary API for solving Letter Boxed
//!
//! # Example
//!
//! ```rust
//! use letter_boxed::solver::solutions::{Solver, SolveParams};
//! use letter_boxed::solver::lexicon::{Lexicon, LEXICON_PATH};
//!
//! fn main() {
//!     // Define input parameters
//!     let params = SolveParams {
//!         letters: String::from("abcdefghijklmnop"),
//!     };
//!
//!     // Load a lexicon
//!     let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
//!
//!     // Solve the puzzle
//!     let result = Solver::solve(params, &lexicon);
//!
//!     println!("{:?}", result);
//! }
//! ```
use super::{
    graph::{Graph, Node},
    lexicon::Lexicon,
};
use serde::{Deserialize, Serialize};
use std::time::Instant;
use std::{fmt, time::Duration};

/// Possible errors with Solution parameters
#[derive(Debug, Serialize)]
pub enum ParamsError {
    GameSize(String),
}

impl fmt::Display for ParamsError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            Self::GameSize(msg) => write!(f, "{}", msg),
            // ...
        }
    }
}

/// Parameters for solving Letter Boxed
#[derive(Debug, Deserialize, Default)]
pub struct SolveParams {
    pub letters: String,
}

impl SolveParams {
    pub fn new(letters: &str) -> Result<Self, ParamsError> {
        Ok(SolveParams {
            letters: letters.to_string(),
        })
    }
    pub fn validate(&self) -> Result<(), ParamsError> {
        if self.letters.len() % 4 != 0 {
            return Err(ParamsError::GameSize(
                "Game size must be a multiple of 4".to_string(),
            ));
        }
        Ok(())
    }
}

/// Represents a solution to Letter Boxed
#[derive(Serialize, Debug)]
pub struct Solution<'a> {
    /// List of words forming the solution.
    words: Vec<String>,
    /// Graph representing all explored nodes and edges
    graph: Graph<'a>,
    /// States representing the nodes in the solution path.
    states: Vec<Node>,
}

/// A solver for Letter Boxed
pub struct Solver {}

impl<'a> Solver {
    /// Solves the game based on the given letters and lexicon, returning a Solution object
    pub fn solve(params: SolveParams, lexicon: &'a Lexicon) -> Option<Solution<'a>> {
        // Build graph and use it to get a path to the solution
        let mut g = Graph::from_letters(&params.letters.as_str());
        let node_ids = g.get_node_path(&params.letters.as_str(), lexicon)?;

        // Collect results
        let mut words = vec![];
        let mut states = vec![];
        for i in 0..node_ids.len() {
            if i != node_ids.len() - 1 {
                words.push(g.get_edge(&node_ids[i], &node_ids[i + 1])?.word.to_string());
            }
            states.push(Node::from_id(node_ids[i].clone()));
        }
        // Return successful solution
        Some(Solution {
            words,
            graph: g,
            states,
        })
    }
}

/// Errors that can occur during solution generation.
#[derive(Debug, Serialize)]
pub enum SolutionError {
    /// General error indicating failure in solution generation.
    GENERAL,
}

#[derive(Debug, Serialize)]
pub struct SolutionMeta {
    status: SolutionStatus,
    runtime: Duration,
}

/// Status of a solution.
#[derive(Debug, Serialize)]
enum SolutionStatus {
    /// Indicating a successful solution.
    SUCCESS,
    /// Indicating failure in finding a solution.
    FAIL(SolutionError),
}

/// Result of a solution attempt.
#[derive(Debug, Serialize)]
pub struct SolutionResult<'a> {
    /// The solution if found.
    solution: Option<Solution<'a>>,
    /// Status of the solution attempt.
    meta: SolutionMeta,
}

impl<'a> SolutionResult<'a> {
    /// Generates a solution result from the given parameters and lexicon.
    pub fn from_params(params: SolveParams, lexicon: &Lexicon) -> SolutionResult {
        // Solve the puzzle and compute runtime
        // TODO: more expressive instrumentation of solve
        //       that returns an instance of SolutionMeta
        let now = Instant::now();
        let solver = Solver::solve(params, lexicon);
        let runtime = Instant::now() - now;

        if let Some(solution) = solver {
            SolutionResult {
                solution: Some(solution),
                meta: SolutionMeta {
                    status: SolutionStatus::SUCCESS,
                    runtime: runtime,
                },
            }
        } else {
            // Failed solve
            SolutionResult {
                solution: None,
                meta: SolutionMeta {
                    status: SolutionStatus::FAIL(SolutionError::GENERAL),
                    runtime: runtime,
                },
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::Solver;
    use crate::solver::lexicon::{Lexicon, LEXICON_PATH};
    use crate::solver::solutions::SolveParams;
    use crate::solver::words::random_string;

    #[test]
    fn graph_search_solve() {
        // Uncomment the appropriate letters for testing

        // Example game
        // let letters = "uigaangbpiam";

        // Random letters
        // let letters = "asoignfhjudlrueusidorptoeuricsbndfhwquitehds";

        // March 10 '24
        // let letters = "ingkphsratec";

        // March 12 '24
        // let letters = "rvheaipnwgmo";

        let letters = random_string(12);
        let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
        let params = SolveParams::new(letters.as_str()).unwrap();
        let solution = Solver::solve(params, &lexicon);
        println!("{:?}", solution);
    }
}
