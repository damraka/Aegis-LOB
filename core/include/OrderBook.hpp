#ifndef ORDERBOOK_HPP
#define ORDERBOOK_HPP

#include "Limit.hpp"
#include <map>
#include <unordered_map>
#include <functional>
#include <iostream>
#include <list>

class OrderBook {
private:
    // Sorted maps to maintain price priority
    // Asks: Ascending (Lowest price first)
    // Bids: Descending (Highest price first)
    std::map<double, Limit> asks;
    std::map<double, Limit, std::greater<double>> bids;

    // THE HEART: Fast lookup/cancellation using iterator tracking.
    // Maps OrderID to its exact position in the linked list for O(1) access.
    std::unordered_map<uint64_t, std::list<Order>::iterator> orderMap;
    std::unordered_map<uint64_t, double> orderPriceMap; // Necessary to know which price level to delete from

public:
    double getBestBid() const {
        if (bids.empty()) return 0.0;
        return bids.begin()->first; 
    }

    double getBestAsk() const {
        if (asks.empty()) return 0.0;
        return asks.begin()->first; 
    }

    double getMidPrice() const {
        double bb = getBestBid();
        double ba = getBestAsk();
        if (bb == 0.0 || ba == 0.0) return 0.0;
        return (bb + ba) / 2.0;
    }

    void addOrder(Order order) {
        if (order.side == Side::BUY) {
            handleBuyOrder(order);
        } else {
            handleSellOrder(order);
        }
    }

    // Cancel an order by its unique ID
    // Uses the orderMap to perform the operation in O(1) time complexity.
    void cancelOrder(uint64_t orderId) {
        if (orderMap.find(orderId) == orderMap.end()) return;

        double price = orderPriceMap[orderId];
        Side side = (*orderMap[orderId]).side;

        if (side == Side::BUY) {
            bids.at(price).orders.erase(orderMap[orderId]);
            if (bids.at(price).orders.empty()) bids.erase(price);
        } else {
            asks.at(price).orders.erase(orderMap[orderId]);
            if (asks.at(price).orders.empty()) asks.erase(price);
        }

        orderMap.erase(orderId);
        orderPriceMap.erase(orderId);
        std::cout << "Order " << orderId << " canceled successfully." << std::endl;
    }

private:
    void handleBuyOrder(Order order) {
        // 1. MATCHING ENGINE
        // Since asks are sorted in ascending order, begin() always provides the best ask price.
        while (order.quantity > 0 && !asks.empty() && order.price >= asks.begin()->first) {
            auto& bestAskLimit = asks.begin()->second;
            
            while (order.quantity > 0 && !bestAskLimit.orders.empty()) {
                auto& sittingOrder = bestAskLimit.orders.front();
                uint32_t matchQty = std::min(order.quantity, sittingOrder.quantity);

                // A TRADE OCCURRED!
                std::cout << "TRADE: Buy Order " << order.id << " matched with Sell Order " 
                          << sittingOrder.id << " | Qty: " << matchQty << " @ Price: " << sittingOrder.price << std::endl;

                order.quantity -= matchQty;
                sittingOrder.quantity -= matchQty;
                bestAskLimit.totalVolume -= matchQty;

                if (sittingOrder.quantity == 0) {
                    orderMap.erase(sittingOrder.id);
                    orderPriceMap.erase(sittingOrder.id);
                    bestAskLimit.orders.pop_front();
                }
            }

            if (bestAskLimit.orders.empty()) {
                asks.erase(asks.begin());
            }
        }

        // 2. RESIDUAL ORDER
        // If the order is not fully filled, add the remaining quantity to the bid side.
        if (order.quantity > 0) {
            if (bids.find(order.price) == bids.end()) {
                bids.emplace(order.price, Limit(order.price));
            }
            bids.at(order.price).addOrder(order);
            orderMap[order.id] = --bids.at(order.price).orders.end();
            orderPriceMap[order.id] = order.price;
        }
    }

    void handleSellOrder(Order order) {
        // 1. MATCHING ENGINE (Against Bids)
        // Since bids are sorted in descending order (std::greater), 
        // begin() provides the highest bidder (Best Bid).
        while (order.quantity > 0 && !bids.empty() && order.price <= bids.begin()->first) {
            auto& bestBidLimit = bids.begin()->second;
            
            while (order.quantity > 0 && !bestBidLimit.orders.empty()) {
                auto& sittingOrder = bestBidLimit.orders.front();
                uint32_t matchQty = std::min(order.quantity, sittingOrder.quantity);

                std::cout << "TRADE: Sell Order " << order.id << " matched with Buy Order " 
                          << sittingOrder.id << " | Qty: " << matchQty << " @ Price: " << sittingOrder.price << std::endl;

                order.quantity -= matchQty;
                sittingOrder.quantity -= matchQty;
                bestBidLimit.totalVolume -= matchQty;

                if (sittingOrder.quantity == 0) {
                    orderMap.erase(sittingOrder.id);
                    orderPriceMap.erase(sittingOrder.id);
                    bestBidLimit.orders.pop_front();
                }
            }

            if (bestBidLimit.orders.empty()) {
                bids.erase(bids.begin());
            }
        }

        // 2. RESIDUAL ORDER (Add remaining to Asks)
        if (order.quantity > 0) {
            if (asks.find(order.price) == asks.end()) {
                asks.emplace(order.price, Limit(order.price));
            }
            asks.at(order.price).addOrder(order);
            orderMap[order.id] = --asks.at(order.price).orders.end();
            orderPriceMap[order.id] = order.price;
        }
    }
};

#endif