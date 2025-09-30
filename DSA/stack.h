//
//  stack.h
//  DSA
//
//  Created by Sebastian Rosas Maciel on 9/29/25.
//

#ifndef stack_h
#define stack_h

class Stack {
private:
    int *arr;
    int top;
    int capacity;

public:
    Stack(int size);
    ~Stack();
    void push(int element);
    int pop();
    int peek();
    bool isEmpty();
    int getSize();
};

#endif
