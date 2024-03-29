// Solutions
//
// A module for interactions with the Letter Boxed solver server

const SERVER_URL = 'http://localhost:3000';
import { StatusCodes } from 'http-status-codes';

export interface RunTime {
	secs: number;
	nanos: number;
}

export class SolverClient {
	// Fetches the solution for a given set of letters
	async solve(letters: string): Promise<any> {
		if (letters.length === 0) {
			return Promise.reject('No letters provided');
		}
		const response = await fetch(`${SERVER_URL}/solve?letters=${letters}`);
		if (response.status === StatusCodes.BAD_REQUEST) {
			return Promise.reject(`Input Error: ${await response.text()}`);
		}
		if (response.status === StatusCodes.INTERNAL_SERVER_ERROR) {
			return Promise.reject(`Internal Server Error: ${await response.text()}`);
		}
		const json = await response.json();
		// Solution Failures
		if (json.solution === null) {
			return Promise.reject("Solver Failure");
		}

		return json;
	}
}
