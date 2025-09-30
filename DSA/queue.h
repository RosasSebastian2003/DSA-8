//
//  queue.h
//  DSA
//
//  Created by Sebastian Rosas Maciel on 9/29/25.
//

#ifndef queue_h
#define queue_h

class Queue {
private:
    int *arr;
    int front, rear, capacity, size;

public:
    Queue(int size);
    ~Queue();
    void enqueue(int element);
    int dequeue();
    int getFront();
    bool isEmpty();
    int getSize();
};

#endif
