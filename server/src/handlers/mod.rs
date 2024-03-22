//! Various handlers for webserver API

use poem::{
    error::NotFoundError, error::ParseQueryError, handler, http::StatusCode, web::Query,
    IntoResponse, Response, Result,
};

use serde::{Deserialize, Serialize};
use serde_json::json;

use crate::solver::{
    graph::Graph,
    lexicon::{Lexicon, LEXICON_PATH},
};

#[derive(Debug, Deserialize)]
struct SolveParams {
    letters: String,
}

#[derive(Serialize, Debug)]
struct Solution<'a> {
    words: Vec<String>,
    graph: Graph<'a>,
}

impl<'a> IntoResponse for Solution<'a> {
    fn into_response(self) -> Response {
        Response::builder().body(json!(self).to_string())
    }
}

#[handler]
pub fn handle_solve(res: Result<Query<SolveParams>>) -> Result<impl IntoResponse> {
    // TODO: figure out how to keep this in app memory instead of reloading
    let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
    match res {
        Ok(Query(params)) => {
            let mut g = Graph::from_letters(&params.letters);
            let words = g.solve(&params.letters, &lexicon).unwrap();
            let soln = Solution {
                words: words.clone(),
                graph: g,
            };
            Ok(soln.into_response())
        }
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
