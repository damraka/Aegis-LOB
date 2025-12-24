#include "../include/OrderBook.hpp"
#include <iostream>

int main() {
    OrderBook ob;

    std::cout << "--- Aegis-LOB: Matching Engine Stress Test Initiated ---" << std::endl;

    // 1. Add Liquidity (Asks)
    // Adding limit sell orders to the book
    ob.addOrder(Order(1, 100.5, 10, Side::SELL, 1000));
    ob.addOrder(Order(2, 101.0, 5, Side::SELL, 1001));

    std::cout << "[INFO] Liquidity added: 10 units @ 100.5, 5 units @ 101.0" << std::endl;

    // 2. Passive Order (Adding to Bids)
    // This order does not cross the spread, so it stays in the book.
    std::cout << "\n[ACTION] Sending Passive Buy Order (5 units @ 99.0)..." << std::endl;
    ob.addOrder(Order(3, 99.0, 5, Side::BUY, 1002));

    // 3. Aggressive Order (Triggering the Matching Engine)
    // This order crosses the spread (102.0 > 100.5) and should sweep the sellers.
    std::cout << "\n[ACTION] Sending Aggressive Buy Order (12 units @ 102.0)..." << std::endl;
    ob.addOrder(Order(4, 102.0, 12, Side::BUY, 1003));

    // 4. Cancellation Test
    // Testing the O(1) cancellation logic using the iterator map.
    std::cout << "\n[ACTION] Canceling Sell Order ID: 2..." << std::endl;
    ob.cancelOrder(2);

    std::cout << "\n--- Aegis-LOB: Test Sequence Completed ---" << std::endl;
    return 0;
}