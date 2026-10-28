#include <iostream>
#include <vector>
#include <string>
#include <numeric>

namespace CodeFlow::Demo {

template <typename T>
class VectorMetrics {
public:
	explicit VectorMetrics(std::vector<T> values) : data_(std::move(values)) {}

	T compute_sum() const {
		return std::accumulate(data_.begin(), data_.end(), static_cast<T>(0));
	}

	size_t count() const {
		return data_.size();
	}

private:
	std::vector<T> data_;
};

} // namespace CodeFlow::Demo

int main() {
	std::vector<int> numbers = { 10, 20, 30, 40, 50 };
	CodeFlow::Demo::VectorMetrics<int> metrics(numbers);

	std::cout << "Sum: " << metrics.compute_sum() << std::endl;
	std::cout << "Count: " << metrics.count() << std::endl;

	return 0;
}
