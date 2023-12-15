#!/usr/bin/env kotlin

import java.io.File
import kotlin.math.max

typealias Input = Map<Int, List<Pair<String, Int>>>

val inputFilePath = File("input.txt")

val colorMaxes = mapOf(
    "red" to 12,
    "green" to 13,
    "blue" to 14,
)
val colors = colorMaxes.keys

val regexColorCount = Regex("(\\d+)\\s+(${colors.joinToString("|")})")


fun readInput(): Input {
    val fileString = inputFilePath.readText()
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


fun solve1(input: Input): Int =
    input.filter {
        (_, pulls) -> pulls.all {
            (color, count) -> count <= colorMaxes[color]!!
        }
    }.map { (gameNum, _) -> gameNum }.sum()


fun solve2(input: Input): Int {
    var totalPower = 0
    for (pulls in input.values) {
        val biggestSeen = HashMap<String, Int>().withDefault { 0 }
        for ((color, count) in pulls) {
            val bestPrev = biggestSeen.getValue(color)
            biggestSeen[color] = max(bestPrev, count)
        }
        val power = colors.map { color -> biggestSeen.getValue(color) }.reduce(Int::times)
        totalPower += power
    }
    return totalPower
}


//fun solve2(input: Input): Int =
//    input.values.sumOf {
//        pulls -> colors.map {
//            targetColor -> pulls.filter {
//                (color, _) -> color == targetColor
//            }.maxOfOrNull { (_, count) -> count } ?: 0
//        }.reduce(Int::times)
//    }


// main
val input = readInput()
val answer1 = solve1(input)
println(answer1)
val answer2 = solve2(input)
println(answer2)
