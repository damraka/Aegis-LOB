#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../core/include/OrderBook.hpp"

namespace py = pybind11;

PYBIND11_MODULE(aegis_lob, m) {
    py::enum_<Side>(m, "Side")
        .value("BUY", Side::BUY)
        .value("SELL", Side::SELL);

    py::class_<Order>(m, "Order")
        .def(py::init<uint64_t, double, uint32_t, Side, uint64_t>());

    py::class_<OrderBook>(m, "OrderBook")
        .def(py::init<>())
        .def("add_order", &OrderBook::addOrder)
        .def("cancel_order", &OrderBook::cancelOrder)
        .def("get_best_bid", &OrderBook::getBestBid)
        .def("get_best_ask", &OrderBook::getBestAsk)
        .def("get_mid_price", &OrderBook::getMidPrice);
}