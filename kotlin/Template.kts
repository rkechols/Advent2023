#!/usr/bin/env kotlin

import java.io.File

typealias Input = String  // feel free to change per-problem; whatever structure is easiest

val inputFilePath = "input.txt"


fun readInput(): Input = File(inputFilePath).readText()


fun solve(input: Input): Any {
    return input  // TODO
}


// main
val input = readInput()
val answer = solve(input)
println(answer)
