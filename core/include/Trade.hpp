#include <iostream>
#include <string>

struct Trade {
    uint64_t buyerId;
    uint64_t sellerId;
    double price;
    uint32_t quantity;
    uint64_t timestamp;
};