import * as fs from "fs";

type Input = string;  // feel free to change per-problem; whatever structure is easiest

const INPUT_FILE_PATH = "input.txt";


function readInput(): Input {
    return fs.readFileSync(INPUT_FILE_PATH, "utf-8");
}


function solve(input: Input): any {
    return input;  // TODO
}


function main() {
    const input = readInput();
    const answer = solve(input);
    console.log(answer);
}


main();
