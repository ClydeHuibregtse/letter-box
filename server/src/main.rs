pub mod handlers;
pub mod solver;

use handlers::handle_solve;
use poem::endpoint::EndpointExt;
use poem::middleware::Cors;
use poem::{get, listener::TcpListener, Result, Route, Server};

#[tokio::main(flavor = "current_thread")]
pub async fn main() -> Result<(), std::io::Error> {
    let app = Route::new().at("/solve", get(handle_solve));

    Server::new(TcpListener::bind("0.0.0.0:3000"))
        // TODO: fix CORS requirements
        .run(app.with(Cors::new()))
        .await
}
