#!/usr/bin/env kotlin

import java.io.File

val symEmpty = '.'
val symGear = '*'

typealias Input = List<List<Char>>

val inputFilePath = File("input.txt")

fun readInput(): Input = inputFilePath.readLines().map {
    line -> line.trim().toList()
}


fun isSymbol(s: Char) = !(s.isDigit() || s == symEmpty)


fun countDigits(row: List<Char>): Int {
    assert(row[0].isDigit())
    for ((i, s) in row.drop(1).withIndex()) {
        if (!s.isDigit()) {
            return i + 1
        }
    }
    return row.size
}

class Solver(input: Input) {
    private val input = input.map { row -> row.toTypedArray() }.toTypedArray()

    private fun hasSymbolNeighbor(r: Int, cStart: Int, n: Int): Boolean {
        var rowsToCheck = listOf(r - 1, r, r + 1).filter { it in input.indices }
        // left bookend
        val cLeft = cStart - 1
        if (cLeft >= 0) {
            for (newR in rowsToCheck) {
                if (isSymbol(input[newR][cLeft])) {
                    return true
                }
            }
        }
        // right bookend
        val cRight = cStart + n
        if (cRight < input[0].size) {
            for (newR in rowsToCheck) {
                if (isSymbol(input[newR][cRight])) {
                    return true
                }
            }
        }
        // all along the number
        rowsToCheck = rowsToCheck.filter { it != r }
        for (newC in cStart until cStart + n) {
            for (newR in rowsToCheck) {
                if (isSymbol(input[newR][newC])) {
                    return true
                }
            }
        }
        // nothing found
        return false
    }

    fun solve1(): Int {
        val data = input.map { row -> row.copyOf() }.toTypedArray()
        var total = 0
        for (r in data.indices) {
            for (c in data[0].indices) {
                if (data[r][c].isDigit()) {
                    val nDigits = countDigits(data[r].drop(c))
                    if (hasSymbolNeighbor(r, c, nDigits)) {
                        val num = data[r].sliceArray(c until c + nDigits)
                            .joinToString("")
                            .toInt()
                        total += num
                    }
                    for (i in c until c + nDigits) {
                        data[r][i] = symEmpty
                    }
                }
            }
        }
        return total
    }

    private fun collectAdjacentNumbers(r: Int, c: Int): List<Int> {
        val data = input.map { row -> row.copyOf() }.toTypedArray()
        val adjacentNumbers = mutableListOf<Int>()
        for (rShift in listOf(-1, 0, 1)) {
            val newR = r + rShift
            for (cShift in listOf(-1, 0, 1)) {
                if (rShift == 0 && cShift == 0) {
                    continue
                }
                val newC = c + cShift
                if (data[newR][newC].isDigit()) {
                    var cStart = newC
                    while (cStart > 0 && data[newR][cStart - 1].isDigit()) {
                        cStart--
                    }
                    val nDigits = countDigits(data[newR].drop(cStart))
                    val num = data[newR].sliceArray(cStart until cStart + nDigits)
                        .joinToString("")
                        .toInt()
                    adjacentNumbers.add(num)
                    for (i in cStart until cStart + nDigits) {
                        data[newR][i] = symEmpty
                    }
                }
            }
        }
        return adjacentNumbers
    }

    fun solve2(): Int {
        var total = 0
        for (r in input.indices) {
            for (c in input[0].indices) {
                if (input[r][c] == symGear) {
                    val adjacentNumbers = collectAdjacentNumbers(r, c)
                    if (adjacentNumbers.size == 2) {
                        val gearRatio = adjacentNumbers[0] * adjacentNumbers[1]
                        total += gearRatio
                    }
                }
            }
        }
        return total
    }
}


val input = readInput()
val solver = Solver(input)
val answer1 = solver.solve1()
println(answer1)
val answer2 = solver.solve2()
println(answer2)
