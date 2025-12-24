#include <iostream>
#include <string>

enum class Side { BUY, SELL };

struct Order {
    uint64_t id;       
    double price;       
    uint32_t quantity; 
    Side side;       
    uint64_t timestamp;

    // Constructor
    Order(uint64_t _id, double _p, uint32_t _q, Side _s, uint64_t _t)
        : id(_id), price(_p), quantity(_q), side(_s), timestamp(_t) {}
};