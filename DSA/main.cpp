//
//  main.cpp
//  DSA
//
//  Created by Sebastian Rosas Maciel on 9/29/25.
//

#include <iostream>
#include "stack.h"
#include "queue.h"
#include "hash_map.h"

int main(int argc, const char * argv[]) {
    
    Stack stack(5);
    std::cout << "Stack" << std::endl;
    stack.push(100);
    stack.push(200);
    stack.push(300);
    std::cout << "Eliminacion de elementos: ";
    while (!stack.isEmpty()) {
        std::cout << stack.pop() << " " << std::endl;
    }
    std::cout << std::endl;
    
    Queue queue(5);
    std::cout << "Cola" << std::endl;
    queue.enqueue(100);
    queue.enqueue(200);
    queue.enqueue(300);
    std::cout << "Eliminacion de elementos ";
    while (!queue.isEmpty()) {
        std::cout << queue.dequeue() << " " << std::endl;
    }
    std::cout << std::endl;
    
    HashMap<std::string, int> scores;
    std::cout << "Hash Map" << std::endl;
    scores.insert("Alice", 95);
    scores.insert("Bob", 87);
    scores.insert("Charlie", 92);
    
    auto score = scores.get("Alice");
    
    if (score.has_value()) { // Comprobar que la llave tenga un valor
        std::cout << "Alice: " << score.value() << std::endl;
    }
    
    // ctualizar valor de Alice
    scores.insert("Alice", 98);
    score = scores.get("Alice");
    if (score.has_value()) {
        std::cout << "Se actualizo la calificacion de Alice: " << score.value() << std::endl;
    }
}
