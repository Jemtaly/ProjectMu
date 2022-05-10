#pragma once
#include <algorithm>
#include <string>
#include <vector>
class Rational {
private:
	int n;
	unsigned int d;
	void reduce() {
		unsigned int t;
		for (unsigned int a = n < 0 ? -n : n, b = d; t = a, b; a = b, b = t % b)
			;
		if (t)
			n /= t, d /= t;
	}
public:
	Rational &set(int const &numerator = 0, int const &denominator = 1) {
		if (d < 0) {
			n = -numerator;
			d = -denominator;
		} else {
			n = numerator;
			d = denominator;
		}
		reduce();
		return *this;
	}
	Rational(int const &numerator = 0, int const &denominator = 1) {
		set(numerator, denominator);
	}
	Rational &operator=(int const &numerator) {
		return set(numerator);
	}
	auto const &numerator() const {
		return n;
	}
	auto const &denominator() const {
		return d;
	}
	int floor() const {
		return d ? n < 0 ? (n + 1) / d - 1 : n / d : 0;
	}
	double value() const {
		return (double)n / d;
	}
	operator int() const {
		return floor();
	}
	operator double() const {
		return value();
	}
	friend Rational operator+(Rational const &);
	friend Rational operator-(Rational const &);
	friend Rational operator~(Rational const &);
	friend Rational operator+(Rational const &, Rational const &);
	friend Rational operator+(Rational const &, int const &);
	friend Rational operator+(int const &, Rational const &);
	friend Rational operator-(Rational const &, Rational const &);
	friend Rational operator-(Rational const &, int const &);
	friend Rational operator-(int const &, Rational const &);
	friend Rational operator*(Rational const &, Rational const &);
	friend Rational operator*(Rational const &, int const &);
	friend Rational operator*(int const &, Rational const &);
	friend Rational operator/(Rational const &, Rational const &);
	friend Rational operator/(Rational const &, int const &);
	friend Rational operator/(int const &, Rational const &);
	friend Rational operator%(Rational const &, Rational const &);
	friend Rational operator%(Rational const &, int const &);
	friend Rational operator%(int const &, Rational const &);
	friend bool operator==(Rational const &, Rational const &);
	friend bool operator==(Rational const &, int const &);
	friend bool operator==(int const &, Rational const &);
	friend bool operator>=(Rational const &, Rational const &);
	friend bool operator>=(Rational const &, int const &);
	friend bool operator>=(int const &, Rational const &);
	friend bool operator<=(Rational const &, Rational const &);
	friend bool operator<=(Rational const &, int const &);
	friend bool operator<=(int const &, Rational const &);
	friend bool operator!=(Rational const &, Rational const &);
	friend bool operator!=(Rational const &, int const &);
	friend bool operator!=(int const &, Rational const &);
	friend bool operator>(Rational const &, Rational const &);
	friend bool operator>(Rational const &, int const &);
	friend bool operator>(int const &, Rational const &);
	friend bool operator<(Rational const &, Rational const &);
	friend bool operator<(Rational const &, int const &);
	friend bool operator<(int const &, Rational const &);
};
Rational operator+(Rational const &r) {
	return Rational(r.n, r.d);
}
Rational operator-(Rational const &r) {
	return Rational(-r.n, r.d);
}
Rational operator~(Rational const &r) {
	return Rational(r.d, r.n);
}
Rational operator+(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.d + r2.n * r1.d, r1.d * r2.d);
}
Rational operator+(Rational const &r, int const &n) {
	return Rational(r.n + n * r.d, r.d);
}
Rational operator+(int const &n, Rational const &r) {
	return Rational(r.n + n * r.d, r.d);
}
Rational operator-(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.d - r2.n * r1.d, r1.d * r2.d);
}
Rational operator-(Rational const &r, int const &n) {
	return Rational(r.n - n * r.d, r.d);
}
Rational operator-(int const &n, Rational const &r) {
	return Rational(r.n - n * r.d, r.d);
}
Rational operator*(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.n, r1.d * r2.d);
}
Rational operator*(Rational const &r, int const &n) {
	return Rational(r.n * n, r.d);
}
Rational operator*(int const &n, Rational const &r) {
	return Rational(r.n * n, r.d);
}
Rational operator/(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.d, r1.d * r2.n);
}
Rational operator/(Rational const &r, int const &n) {
	return Rational(r.n, r.d * n);
}
Rational operator/(int const &n, Rational const &r) {
	return Rational(r.n, r.d * n);
}
Rational operator%(Rational const &r1, Rational const &r2) {
	return r1 - (r1 / r2).floor() * r2;
}
Rational operator%(Rational const &r, int const &n) {
	return r % Rational(n);
}
Rational operator%(int const &n, Rational const &r) {
	return Rational(n) % r;
}
bool operator==(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n == 0;
}
bool operator==(Rational const &r, int const &n) {
	return (r - n).n == 0;
}
bool operator==(int const &n, Rational const &r) {
	return (r - n).n == 0;
}
bool operator!=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n != 0;
}
bool operator!=(Rational const &r, int const &n) {
	return (r - n).n != 0;
}
bool operator!=(int const &n, Rational const &r) {
	return (r - n).n != 0;
}
bool operator>=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n >= 0;
}
bool operator>=(Rational const &r, int const &n) {
	return (r - n).n >= 0;
}
bool operator>=(int const &n, Rational const &r) {
	return (r - n).n >= 0;
}
bool operator<=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n <= 0;
}
bool operator<=(Rational const &r, int const &n) {
	return (r - n).n <= 0;
}
bool operator<=(int const &n, Rational const &r) {
	return (r - n).n <= 0;
}
bool operator>(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n > 0;
}
bool operator>(Rational const &r, int const &n) {
	return (r - n).n > 0;
}
bool operator>(int const &n, Rational const &r) {
	return (r - n).n > 0;
}
bool operator<(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n < 0;
}
bool operator<(Rational const &r, int const &n) {
	return (r - n).n < 0;
}
bool operator<(int const &n, Rational const &r) {
	return (r - n).n < 0;
}
template <typename T>
Rational &operator+=(Rational &r, T const &x) {
	return r = r + x;
}
template <typename T>
Rational &operator-=(Rational &r, T const &x) {
	return r = r - x;
}
template <typename T>
Rational &operator*=(Rational &r, T const &x) {
	return r = r * x;
}
template <typename T>
Rational &operator/=(Rational &r, T const &x) {
	return r = r / x;
}
template <typename T>
Rational &operator%=(Rational &r, T const &x) {
	return r = r % x;
}
