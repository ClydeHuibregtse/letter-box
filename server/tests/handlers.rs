// use poem::web::TestRequest;
use letter_boxed::handlers::handle_solve;
use poem::test::TestClient;

#[tokio::test]
async fn test_solve_handler() {
    // // Full round-trip for solving a puzzle
    // // March 12 '24
    let letters = "rvheaipnwgmo";
    let resp = TestClient::new(handle_solve)
        .get("/solve")
        .query("letters", &letters)
        .send()
        .await;
    resp.assert_status_is_ok();
}
