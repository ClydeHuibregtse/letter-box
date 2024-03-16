mod solver;

use poem::{
    error::ParseQueryError, get, handler, http::StatusCode, listener::TcpListener, web::Query,
    IntoResponse, Response, Result, Route, Server,
};
use serde::Deserialize;
use solver::graph::Graph;
use solver::lexicon::{Lexicon, LEXICON_PATH};
use solver::words::random_string;

#[derive(Debug, Deserialize)]
struct SolveParams {
    letters: String,
}

#[handler]
fn solve(res: Result<Query<SolveParams>>) -> Result<impl IntoResponse> {
    match res {
        Ok(Query(params)) => Ok(params.letters.into_response()),
        Err(err) if err.is::<ParseQueryError>() => Ok(Response::builder()
            .status(StatusCode::INTERNAL_SERVER_ERROR)
            .body(err.to_string())),
        Err(err) => Err(err),
    }
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), std::io::Error> {
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
