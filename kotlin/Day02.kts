#!/usr/bin/env kotlin

import java.io.File

typealias Input = Map<Int, List<Pair<String, Int>>>

val inputFilePath = "input.txt"

val colorMaxes = mapOf(
    "red" to 12,
    "green" to 13,
    "blue" to 14,
)
val colors = colorMaxes.keys

val regexColorCount = Regex("(\\d+)\\s+(${colors.joinToString("|")})")


fun readInput(): Input {
    val fileString = File(inputFilePath).readText()
    val data = HashMap<Int, List<Pair<String, Int>>>()
    val regexGameNum = Regex("^Game (\\d+):")
    for (lineRaw in fileString.lines()) {
        val line = lineRaw.trim()
        if (line.isEmpty()) {
            continue
        }
        val matchGameNum = regexGameNum.find(line)!!.groups[1]!!
        val gameNum = Integer.parseInt(matchGameNum.value)
        val pullsRaw = line.substring(matchGameNum.range.last + 1).split(",", ";")
        val pulls = pullsRaw.mapNotNull { pullRaw -> regexColorCount.find(pullRaw) }
            .map { match -> Pair(match.groups[2]!!.value, Integer.parseInt(match.groups[1]!!.value)) }
        data[gameNum] = pulls
    }
    return data
}


fun solve(input: Input): Int {
    return input.filter {
        (_, pulls) -> pulls.all {
            (color, count) -> count <= colorMaxes[color]!!
        }
    }.map { (gameNum, _) -> gameNum }.sum()
}


// main
val input = readInput()
val answer = solve(input)
println(answer)
