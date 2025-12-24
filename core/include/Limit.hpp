#ifndef LIMIT_HPP
#define LIMIT_HPP

#include "Order.hpp"
#include <list>

struct Limit {
    double price;
    uint32_t totalVolume;
    std::list<Order> orders; // FIFO sırasıyla emirler

    Limit(double p) : price(p), totalVolume(0) {}

    // Yeni emir ekleme (Listenin sonuna)
    void addOrder(const Order& order) {
        totalVolume += order.quantity;
        orders.push_back(order);
    }
};

#endif