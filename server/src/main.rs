use poem::{
    get, handler, listener::TcpListener, web::{Path, Query}, IntoResponse, Result, Route, Server, Response,
    error::ParseQueryError, http::StatusCode,
};
use serde::Deserialize;


#[derive(Debug, Deserialize)]
struct SolveParams {
    letters: String
}

#[handler]
fn solve(
    res: Result<Query<SolveParams>>
) -> Result<impl IntoResponse> {
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
    let app = Route::new()
        .at("/solve", get(solve));
    
    Server::new(TcpListener::bind("0.0.0.0:3000"))
      .run(app)
      .await
}