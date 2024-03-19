use std::process::ExitStatus;

// use poem::web::TestRequest;
use letter_boxed::handlers::handle_solve;
use poem::{
    http::{Method, StatusCode},
    test::TestClient,
};

use poem::Response;

#[tokio::test]
async fn test_solve_handler() {
    println!("KLSJDFLKJSBDFLKSJ");
    // // Full round-trip for solving a puzzle
    // // March 12 '24
    let letters = "rvheaipnwgmo";
    let resp = TestClient::new(handle_solve)
        .get("/solve")
        .query("letters", &letters)
        .send()
        .await;
    resp.assert_status_is_ok();
    resp.assert_text("hello").await;
}
