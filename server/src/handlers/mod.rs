//! Various handlers for webserver API

use poem::{
    error::NotFoundError, error::ParseQueryError, get, handler, http::StatusCode,
    listener::TcpListener, web::Query, Endpoint, IntoResponse, Request, Response, Result, Route,
    Server,
};

use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct SolveParams {
    letters: String,
}

#[handler]
pub fn solve(res: Result<Query<SolveParams>>) -> Result<impl IntoResponse> {
    match res {
        Ok(Query(params)) => Ok(params.letters.into_response()),
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
