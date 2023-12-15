#!/usr/bin/env kotlin

import java.io.File

typealias Input = List<String>

val inputFilePath = File("input.txt")


fun readInput(): Input = inputFilePath.readLines()
    .map { line -> line.trim() }
    .filter { line -> line.isNotEmpty() }


fun solve1(input: Input): Int {
    val digitRegex = Regex("\\d")
    var total = 0
    for (line in input) {
        val first = digitRegex.find(line)!!.value
        val last = digitRegex.find(line.reversed())!!.value
        val number = Integer.parseInt("${first}${last}")
        total += number
    }
    return total
}


val digitsByName = mapOf(
    "one" to "1",
    "two" to "2",
    "three" to "3",
    "four" to "4",
    "five" to "5",
    "six" to "6",
    "seven" to "7",
    "eight" to "8",
    "nine" to "9",
)


fun toDigit(num: String): String {
    if (num.all { char -> char.isDigit() }) {
        return num
    }
    return digitsByName[num]!!
}


fun solve2(input: Input): Int {
    val unionDigitNames = digitsByName.keys.joinToString("|")
    val regexDigitsForward = Regex("\\d|${unionDigitNames}")
    val regexDigitsBackward = Regex("\\d|${unionDigitNames.reversed()}")
    var total = 0
    for (line in input) {
        val first = regexDigitsForward.find(line)!!.value
        val last = regexDigitsBackward.find(line.reversed())!!.value.reversed()
        val number = Integer.parseInt("${toDigit(first)}${toDigit(last)}")
        total += number
    }
    return total
}


// main
val input = readInput()
val answer1 = solve1(input)
println(answer1)
val answer2 = solve2(input)
println(answer2)
