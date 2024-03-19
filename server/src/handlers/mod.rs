//! Various handlers for webserver API

use poem::{
    error::NotFoundError, error::ParseQueryError, get, handler, http::StatusCode,
    listener::TcpListener, web::Query, Endpoint, IntoResponse, Request, Response, Result, Route,
    Server,
};

use serde::{Deserialize, Serialize};
use serde_json::json;

use crate::solver::{
    graph::Graph,
    lexicon::{self, Lexicon, LEXICON_PATH},
};

#[derive(Debug, Deserialize)]
struct SolveParams {
    letters: String,
}

#[derive(Serialize, Deserialize)]
struct Solution {
    words: Vec<String>,
}

impl<'a> IntoResponse for Solution {
    fn into_response(self) -> Response {
        Response::builder().body(json!(self).to_string())
    }
}

#[handler]
pub fn handle_solve(res: Result<Query<SolveParams>>) -> Result<impl IntoResponse> {
    // TODO: figure out how to keep this in app memory instead of reloading
    let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
    println!("{:?}", res);
    match res {
        Ok(Query(params)) => Ok(Solution {
            words: Graph::from_letters(&params.letters)
                .solve(&params.letters, &lexicon)
                .unwrap()
                .clone(),
        }
        .into_response()),
        Err(err) if err.is::<ParseQueryError>() => Ok(Response::builder()
            .status(StatusCode::INTERNAL_SERVER_ERROR)
            .body(err.to_string())),
        Err(err) => Err(err),
    }
}

#[handler]
fn return_err() -> Result<&'static str, NotFoundError> {
    Err(NotFoundError)
}
