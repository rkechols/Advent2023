import * as fs from "fs";
import { stringify } from "querystring";

type Pair<T, U> = [T, U];
type Input = Map<number, Array<Pair<string, number>>>;

const INPUT_FILE_PATH = "input.txt";

const COLOR_MAXES = {
    red: 12,
    green: 13,
    blue: 14,
}
const COLORS = Object.keys(COLOR_MAXES);


function readInput(): Input {
    const fileString = fs.readFileSync(INPUT_FILE_PATH, "utf-8");
    const data: Input = new Map();
    for (let line of fileString.split("\n")) {
        line = line.trim();
        if (!line) {
            continue;
        }
        const regexGameNum = /Game (\d+):/g;
        const gameNumMatch = regexGameNum.exec(line);
        if (gameNumMatch == null) {
            continue;
        }
        const gameNum = parseInt(gameNumMatch[1]);
        const pullsRaw = line.substring(regexGameNum.lastIndex);
        const pulls = Array.from(pullsRaw.matchAll(new RegExp(`(\\d+)\\s+(${COLORS.join("|")})`, "g")))
            .map(match => [match[2], parseInt(match[1])] as Pair<string, number>);
        data.set(gameNum, pulls);
    }
    return data;
}


function solve1(input: Input): number {
    return Array.from(input.entries())
        .filter(([_, pulls]) => pulls.every(
            ([color, count]) => (count <= COLOR_MAXES[color])
        )).map(([gameNum, _]) => gameNum)
        .reduce((total, current) => total + current);
}


function solve2(input: Input): number {
    let totalPower = 0;
    for (const pulls of input.values()) {
        const biggestSeen = new Map<string, number>();
        for (const [color, count] of pulls) {
            const best_prev = biggestSeen.get(color) || 0;
            biggestSeen.set(color, Math.max(best_prev, count));
        }
        const power = COLORS.map(color => biggestSeen.get(color) || 0)
            .reduce((prod, num) => prod * num);
        totalPower += power;
    }
    return totalPower;
}


function main() {
    const input = readInput();
    const answer1 = solve1(input);
    console.log(answer1);
    const answer2 = solve2(input);
    console.log(answer2);
}


main();
