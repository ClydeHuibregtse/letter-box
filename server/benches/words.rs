use divan::{black_box, counter::BytesCount, AllocProfiler, Bencher};
use letter_boxed::solver::graph::Graph;
use letter_boxed::solver::lexicon::{Lexicon, LEXICON_PATH};
use letter_boxed::solver::words::{
    can_make_word, random_english_string, random_string, WordTrajectories, WordTrajectory,
};

fn main() {
    // Run registered benchmarks.
    divan::main();
}

/// Benchmark the increment of WordTrajectory
/// (does this allocate unnecessarily? Should we mutate instead?)
#[divan::bench()]
fn bench_word_trajectories(bencher: Bencher) {
    bencher
        .with_inputs(|| WordTrajectory::new())
        .bench_local_values(|traj| {
            traj.add_index(0);
        });
}

/// Benchmark the end to end computation of valid word trajectories
#[divan::bench(consts = [4, 8, 16, 32, 40, 45])]
fn bench_can_make_word<const SIZES: usize>(bencher: Bencher) {
    bencher
        .with_inputs(|| {
            // Generate a random word and random game board
            (random_string(SIZES / 4), random_string(SIZES))
        })
        .bench_local_refs(|args| {
            let mut trajectories = can_make_word(args.0.as_str(), &args.1);
            trajectories.next();
        });
}

/// Benchmark the end to end computation of valid word trajectories
/// using random strings with English letter distribution
#[divan::bench(consts = [4, 8, 16, 32, 40, 45])]
fn bench_can_make_word_english<const SIZES: usize>(bencher: Bencher) {
    bencher
        .with_inputs(|| {
            // Generate a random word and random game board
            (
                random_english_string(SIZES / 4),
                random_english_string(SIZES),
            )
        })
        .bench_local_refs(|args| {
            let mut trajectories = can_make_word(args.0.as_str(), &args.1);
            trajectories.next();
        });
}

#[divan::bench(consts = [4, 8, 12], sample_count=10)]
fn bench_solve<const SIZES: usize>(bencher: Bencher) {
    let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
    bencher
        .with_inputs(|| {
            // Generate a random game board
            random_string(SIZES)
        })
        .bench_local_refs(|letters| {
            // println!("{:?}", letters);
            let mut g = Graph::from_letters(letters);
            let words = g.solve(letters, &lexicon);
        });
}
