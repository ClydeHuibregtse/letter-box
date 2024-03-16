pub mod handlers;
pub mod solver;

use poem::{
    error::ParseQueryError, get, handler, http::StatusCode, listener::TcpListener, web::Query,
    IntoResponse, Response, Result, Route, Server,
};
use serde::Deserialize;
use solver::graph::Graph;
use solver::lexicon::{Lexicon, LEXICON_PATH};
use solver::words::random_string;

#[tokio::main(flavor = "current_thread")]
pub async fn main() -> Result<(), std::io::Error> {
    let s = 3;
    // let letters = random_string(4 * s);
    let letters = "luykrtioabnw";
    let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
    let mut g = Graph::from_letters(&letters);
    let words = g.solve(&letters, &lexicon);
    println!("{:?}", words);
    Ok(())
    // let app = Route::new()
    //     .at("/solve", get(solve));

    // Server::new(TcpListener::bind("0.0.0.0:3000"))
    //   .run(app)
    //   .await
}
