//
//  stack.cpp
//  DSA
//
//  Created by Sebastian Rosas Maciel on 9/29/25.
//

/*
 Basado en:
 https://medium.com/@RobuRishabh/understanding-how-to-use-stack-queues-c-9f1fc06d1c5e
 */

#include "stack.h"
#include <iostream>

Stack::Stack(int size) {
    arr = new int[size];
    capacity = size;
    top = -1;
}

Stack::~Stack() {
    delete[] arr;
}

void Stack::push(int element) {
    if (top == capacity - 1) {
        return;
    }
    arr[++top] = element;
}

int Stack::pop() {
    if (top == -1) {
        return -1;
    }
    int element = arr[top--];
    return element;
}

int Stack::peek() {
    if (top == -1) {
        return -1;
    }
    
    return arr[top];
}

bool Stack::isEmpty() {
    return top == -1;
}

int Stack::getSize() {
    return top + 1;
}
