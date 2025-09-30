//
//  queue.cpp
//  DSA
//
//  Created by Sebastian Rosas Maciel on 9/29/25.
//

/*
 Basado en:
 https://medium.com/@RobuRishabh/understanding-how-to-use-stack-queues-c-9f1fc06d1c5e
 */

#include "queue.h"
#include <iostream>

Queue::Queue(int size) {
    arr = new int[size];
    capacity = size;
    front = 0;
    rear = -1;
    this->size = 0;
}

// Destructor
Queue::~Queue() {
    delete[] arr;
}

void Queue::enqueue(int element) {
    if (size == capacity) {
        return;
    }
    
    rear = (rear + 1) % capacity;
    arr[rear] = element;
    size++;
}

int Queue::dequeue() {
    if (isEmpty()) {
        return -1;
    }
    
    int element = arr[front];
    front = (front + 1) % capacity;
    size--;
    
    return element;
}

int Queue::getFront() {
    if (isEmpty()) {
        return -1;
    }
    
    return arr[front];
}

bool Queue::isEmpty() {
    return size == 0;
}

int Queue::getSize() {
    return size;
}
