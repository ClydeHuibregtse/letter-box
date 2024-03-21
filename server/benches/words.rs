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
/// Time how long it takes to find one solution for every word
/// in the default lexicon for a random game board
#[divan::bench(consts = [4, 8, 16, 32, 40, 45])]
fn bench_can_make_word<const SIZES: usize>(bencher: Bencher) {
    let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
    bencher
        .with_inputs(|| {
            // Get all words and Generate a random game board
            (lexicon.all(), random_string(SIZES))
        })
        .bench_local_refs(|args| {
            args.0.iter().for_each(|word| {
                let mut trajectories = can_make_word(&word, &args.1);
                trajectories.next();
            })
        });
}

/// Benchmark the end to end computation of valid word trajectories
/// using random strings with English letter distribution
#[divan::bench(consts = [4, 8, 16, 32, 40, 45])]
fn bench_can_make_word_english<const SIZES: usize>(bencher: Bencher) {
    let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
    bencher
        .with_inputs(|| {
            // Get all words and Generate a random game board
            (lexicon.all(), random_english_string(SIZES))
        })
        .bench_local_refs(|args| {
            args.0.iter().for_each(|word| {
                let mut trajectories = can_make_word(&word, &args.1);
                trajectories.next();
            })
        });
}

#[divan::bench(threads=true, consts = [4, 16, 64], max_time=1)]
fn bench_solve<const SIZES: usize>(bencher: Bencher) {
    let lexicon = Lexicon::new(LEXICON_PATH).unwrap();
    bencher
        .with_inputs(|| {
            // Generate a random game board
            random_english_string(SIZES)
        })
        .bench_local_refs(|letters| {
            let mut g = Graph::from_letters(letters);
            let words = g.solve(letters, &lexicon);
        });
}
