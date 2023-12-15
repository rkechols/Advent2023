#!/usr/bin/env kotlin

import java.io.File
import kotlin.math.pow

typealias Input = List<Pair<List<Int>, List<Int>>>

val inputFilePath = File("input.txt")


fun readInput(): Input = inputFilePath.readLines().map { line ->
    val rawHalves = line.split(":")[1].split("|")
    val parsedHalves = rawHalves.map {
        rawHalf -> rawHalf.trim()
            .split(Regex("\\s+"))
            .map { it.toInt() }
    }
    assert(parsedHalves.size == 2)
    val winning = parsedHalves[0]
    val yours = parsedHalves[1]
    winning to yours
}


fun solve1(input: Input): Int = input.sumOf { (winningList, yours) ->
    val winning = winningList.toSet()
    val count = yours.count { num -> num in winning }
    val score = if (count == 0) 0
        else (2.0).pow(count - 1).toInt()
    score
}


fun solve2(input: Input): Int {
    val nCopies = IntArray(input.size) { 1 }
    for ((i, pair) in input.withIndex()){
        val (winningList, yours) = pair
        val winning = winningList.toSet()
        val count = yours.count { num -> num in winning }
        for (iAdd in (i + 1)..(i + count)) {
            nCopies[iAdd] += nCopies[i]
        }
    }
    return nCopies.sum()
}


val input = readInput()
val answer1 = solve1(input)
println(answer1)
val answer2 = solve2(input)
println(answer2)
