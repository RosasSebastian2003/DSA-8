//
//  hash_map.h
//  DSA
//
//  Created by Sebastian Rosas Maciel on 9/29/25.
//

#ifndef hash_map_h
#define hash_map_h

#include <iostream>
#include <list>
#include <vector>
#include <optional>

template<typename K, typename V>
class HashMap {
private:
    struct Entry {
        K key;
        V value;
        
        Entry(const K& k, const V& v) : key(k), value(v) {}
    };
    
    std::vector<std::list<Entry>> table;
    int capacity;
    int size;
    
    int hash(const K& key) const {
        return std::hash<K>{}(key) % capacity;
    }
    
public:
    HashMap(int cap = 8) : capacity(cap), size(0) {
        table.resize(capacity);
    }
    
    void insert(const K& key, const V& value);
    
    std::optional<V> get(const K& key) const;
    
    void remove(const K& key);
    
    int getSize() const { return size; }
    
    int getCapacity() const { return capacity; }
    
    bool isEmpty() const { return size == 0; }
};


template<typename K, typename V>
void HashMap<K, V>::insert(const K& key, const V& value) {
    int idx = hash(key);
    for (auto& entry : table[idx]) {
        if (entry.key == key) {
            entry.value = value;
            return;
        }
    }
    table[idx].emplace_back(key, value);
    ++size;
}

template<typename K, typename V>
std::optional<V> HashMap<K, V>::get(const K& key) const {
    int idx = hash(key);
    for (const auto& entry : table[idx]) {
        if (entry.key == key) return entry.value;
    }
    return std::nullopt;
}

template<typename K, typename V>
void HashMap<K, V>::remove(const K& key) {
    int idx = hash(key);
    for (auto it = table[idx].begin(); it != table[idx].end(); ++it) {
        if (it->key == key) {
            table[idx].erase(it);
            --size;
            return;
        }
    }
}

#endif /* hash_map_h */
