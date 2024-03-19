use divan::{black_box, counter::BytesCount, AllocProfiler, Bencher};
use letter_boxed::solver::graph::Graph;
use letter_boxed::solver::lexicon::{Lexicon, LEXICON_PATH};
use letter_boxed::solver::words::{can_make_word, random_string};

fn main() {
    // Run registered benchmarks.
    divan::main();
}

#[divan::bench(consts = [4, 8, 16, 32])]
fn bench_can_make_word<const SIZES: usize>(bencher: Bencher) {
    bencher
        .with_inputs(|| {
            // Generate a random game board and random word
            (random_string(SIZES), random_string(SIZES))
        })
        .bench_local_refs(|args| {
            let mut trajectories = can_make_word(args.0.as_str(), &args.1);
            while let Some(next) = trajectories.next() {}
        });
}

#[divan::bench(consts = [4, 8, 16, 32, 64], sample_count=10)]
fn bench_solve<const SIZES: usize>(bencher: Bencher) {
    let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
    bencher
        .with_inputs(|| {
            // Generate a random game board
            random_string(SIZES)
        })
        .bench_local_refs(|letters| {
            let mut g = Graph::from_letters(letters);
            let words = g.solve(letters, &lexicon);
        });
}
