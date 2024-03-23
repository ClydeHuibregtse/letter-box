import { SolverClient } from './solutions.ts';
import { describe, it, beforeEach } from 'mocha';
import { expect } from 'chai';

describe('SolverClient', () => {
	let solverClient: SolverClient;

	beforeEach(() => {
		solverClient = new SolverClient();
	});

	describe('solve', () => {
		it('should fail if the length of letters is not a multiple of 4', async () => {
			const letters = 'abcde'; // length is not a multiple of 4
			await solverClient.solve(letters).then(
				(val) => {
					throw new Error('Expected to fail');
				},
				(reason) => expect(reason).to.equal('Input Error: Game size must be a multiple of 4')
			);
		});

		it('should pass if the length of letters is a multiple of 4', async () => {
			const letters = 'abcdefgh'; // length is a multiple of 4
			const response = await solverClient.solve(letters);

			expect(response.meta.status).to.equal('SUCCESS');
			expect(response.solution).to.be.an('object');
		});
	});
});
