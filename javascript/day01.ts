import * as fs from "fs";

type Input = string[];

const INPUT_FILE_PATH = "input.txt";


function readInput(): Input {
    return fs.readFileSync(INPUT_FILE_PATH, "utf-8").split("\n")
        .map(line => line.trim())
        .filter(line => line.length);
}


function reverseString(s: string): string {
    return Array.from(s).reverse().join("");
}


function solve1(input: Input): number {
    const regexDigit = /\d/;
    var total = 0;
    for (const line of input) {
        const firstMatch = line.match(regexDigit);
        if (!firstMatch) {
            throw new Error(line);
        }
        const first = firstMatch[0];
        const lastMatch = reverseString(line).match(regexDigit);
        if (!lastMatch) {
            throw new Error(line);
        }
        const last = lastMatch[0];
        const num = parseInt(`${first}${last}`);
        total += num;
    }
    return total;
}


const DIGITS_BY_NAME = {
    one: "1",
    two: "2",
    three: "3",
    four: "4",
    five: "5",
    six: "6",
    seven: "7",
    eight: "8",
    nine: "9",
};


const regexAllDigits = /^\d+$/;

function toDigit(num: string): string {
    if (regexAllDigits.test(num)) {
        return num;
    }
    return DIGITS_BY_NAME[num];
}


function solve2(input: Input): number {
    const unionDigitNames = Object.keys(DIGITS_BY_NAME).join("|");
    const regexDigitsForward = new RegExp(`\\d|${unionDigitNames}`);
    const regexDigitsBackward = new RegExp(`\\d|${reverseString(unionDigitNames)}`);
    var total = 0;
    for (const line of input) {
        const firstMatch = line.match(regexDigitsForward);
        if (!firstMatch) {
            throw new Error(line);
        }
        const first = firstMatch[0];
        const lastMatch = reverseString(line).match(regexDigitsBackward);
        if (!lastMatch) {
            throw new Error(line);
        }
        const last = reverseString(lastMatch[0]);
        const num = parseInt(`${toDigit(first)}${toDigit(last)}`);
        total += num;
    }
    return total;
}


function main() {
    const input = readInput();
    const answer1 = solve1(input);
    console.log(answer1);
    const answer2 = solve2(input);
    console.log(answer2);
}


main();
