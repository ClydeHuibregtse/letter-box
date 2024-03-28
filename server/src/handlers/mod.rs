//! Various handlers for webserver API

use poem::{
    error::{NotFoundError, ParseQueryError},
    handler,
    http::StatusCode,
    web::Query,
    IntoResponse, Response, Result,
};

use serde_json::json;

use crate::solver::{
    lexicon::{Lexicon, LEXICON_PATH},
    solutions::{SolutionResult, SolveParams},
};

impl<'a> IntoResponse for SolutionResult<'a> {
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
            // Validate params before sending to solver
            println!("Params: {:?}", params);
            match params.validate() {
                Ok(_) => (),
                Err(err) => {
                    return Ok(Response::builder()
                        .status(StatusCode::BAD_REQUEST)
                        .body(err.to_string()));
                }
            }
            let soln = SolutionResult::from_params(params, &lexicon);
            println!("Solution {:?}", soln);

            return Ok(soln.into_response());
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
