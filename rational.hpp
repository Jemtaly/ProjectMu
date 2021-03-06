#pragma once
#include <algorithm>
#include <string>
#include <vector>
class Rational {
private:
	int n;
	unsigned int d;
	void reduce() {
		unsigned int a = n < 0 ? -n : n;
		unsigned int b = d;
		while (b) {
			unsigned int t = a;
			a = b;
			b = t % b;
		}
		if (a) {
			n /= a;
			d /= a;
		}
	}
public:
	Rational(int const &numerator = 0, int const &denominator = 1) {
		if (denominator < 0) {
			n = -numerator;
			d = -denominator;
		} else {
			n = numerator;
			d = denominator;
		}
		reduce();
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
	friend inline Rational operator+(Rational const &);
	friend inline Rational operator-(Rational const &);
	friend inline Rational operator~(Rational const &);
	friend inline Rational operator+(Rational const &, Rational const &);
	friend inline Rational operator+(Rational const &, int const &);
	friend inline Rational operator+(int const &, Rational const &);
	friend inline Rational operator-(Rational const &, Rational const &);
	friend inline Rational operator-(Rational const &, int const &);
	friend inline Rational operator-(int const &, Rational const &);
	friend inline Rational operator*(Rational const &, Rational const &);
	friend inline Rational operator*(Rational const &, int const &);
	friend inline Rational operator*(int const &, Rational const &);
	friend inline Rational operator/(Rational const &, Rational const &);
	friend inline Rational operator/(Rational const &, int const &);
	friend inline Rational operator/(int const &, Rational const &);
	friend inline Rational operator%(Rational const &, Rational const &);
	friend inline Rational operator%(Rational const &, int const &);
	friend inline Rational operator%(int const &, Rational const &);
	friend inline bool operator==(Rational const &, Rational const &);
	friend inline bool operator==(Rational const &, int const &);
	friend inline bool operator==(int const &, Rational const &);
	friend inline bool operator>=(Rational const &, Rational const &);
	friend inline bool operator>=(Rational const &, int const &);
	friend inline bool operator>=(int const &, Rational const &);
	friend inline bool operator<=(Rational const &, Rational const &);
	friend inline bool operator<=(Rational const &, int const &);
	friend inline bool operator<=(int const &, Rational const &);
	friend inline bool operator!=(Rational const &, Rational const &);
	friend inline bool operator!=(Rational const &, int const &);
	friend inline bool operator!=(int const &, Rational const &);
	friend inline bool operator>(Rational const &, Rational const &);
	friend inline bool operator>(Rational const &, int const &);
	friend inline bool operator>(int const &, Rational const &);
	friend inline bool operator<(Rational const &, Rational const &);
	friend inline bool operator<(Rational const &, int const &);
	friend inline bool operator<(int const &, Rational const &);
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
	return Rational(r.n + r.d * n, r.d);
}
Rational operator+(int const &n, Rational const &r) {
	return Rational(r.n + r.d * n, r.d);
}
Rational operator-(Rational const &r1, Rational const &r2) {
	return Rational(r1.n * r2.d - r2.n * r1.d, r1.d * r2.d);
}
Rational operator-(Rational const &r, int const &n) {
	return Rational(r.n - r.d * n, r.d);
}
Rational operator-(int const &n, Rational const &r) {
	return Rational(r.d * n - r.n, r.d);
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
	return Rational(r1.n * r2.d, r2.n * r1.d);
}
Rational operator/(Rational const &r, int const &n) {
	return Rational(r.n, r.d * n);
}
Rational operator/(int const &n, Rational const &r) {
	return Rational(r.d * n, r.n);
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
	return (n - r).n == 0;
}
bool operator!=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n != 0;
}
bool operator!=(Rational const &r, int const &n) {
	return (r - n).n != 0;
}
bool operator!=(int const &n, Rational const &r) {
	return (n - r).n != 0;
}
bool operator>=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n >= 0;
}
bool operator>=(Rational const &r, int const &n) {
	return (r - n).n >= 0;
}
bool operator>=(int const &n, Rational const &r) {
	return (n - r).n >= 0;
}
bool operator<=(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n <= 0;
}
bool operator<=(Rational const &r, int const &n) {
	return (r - n).n <= 0;
}
bool operator<=(int const &n, Rational const &r) {
	return (n - r).n <= 0;
}
bool operator>(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n > 0;
}
bool operator>(Rational const &r, int const &n) {
	return (r - n).n > 0;
}
bool operator>(int const &n, Rational const &r) {
	return (n - r).n > 0;
}
bool operator<(Rational const &r1, Rational const &r2) {
	return (r1 - r2).n < 0;
}
bool operator<(Rational const &r, int const &n) {
	return (r - n).n < 0;
}
bool operator<(int const &n, Rational const &r) {
	return (n - r).n < 0;
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
