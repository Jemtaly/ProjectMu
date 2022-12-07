#pragma once
class Rational {
private:
	int n;
	int d;
	void reduce() {
		int a = n < 0 ? -n : n;
		int b = d;
		while (b) {
			int t = a;
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
	friend inline auto operator<=>(Rational const &, Rational const &);
	friend inline auto operator<=>(Rational const &, int const &);
	friend inline auto operator<=>(int const &, Rational const &);
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
Rational operator+(Rational const &l, Rational const &r) {
	return Rational(l.n * r.d + r.n * l.d, l.d * r.d);
}
Rational operator+(Rational const &l, int const &n) {
	return Rational(l.n + l.d * n, l.d);
}
Rational operator+(int const &n, Rational const &r) {
	return Rational(r.n + r.d * n, r.d);
}
Rational operator-(Rational const &l, Rational const &r) {
	return Rational(l.n * r.d - r.n * l.d, l.d * r.d);
}
Rational operator-(Rational const &l, int const &n) {
	return Rational(l.n - l.d * n, l.d);
}
Rational operator-(int const &n, Rational const &r) {
	return Rational(r.d * n - r.n, r.d);
}
Rational operator*(Rational const &l, Rational const &r) {
	return Rational(l.n * r.n, l.d * r.d);
}
Rational operator*(Rational const &l, int const &n) {
	return Rational(l.n * n, l.d);
}
Rational operator*(int const &n, Rational const &r) {
	return Rational(r.n * n, r.d);
}
Rational operator/(Rational const &l, Rational const &r) {
	return Rational(l.n * r.d, r.n * l.d);
}
Rational operator/(Rational const &l, int const &n) {
	return Rational(l.n, l.d * n);
}
Rational operator/(int const &n, Rational const &r) {
	return Rational(r.d * n, r.n);
}
Rational operator%(Rational const &l, Rational const &r) {
	return l - (l / r).floor() * r;
}
Rational operator%(Rational const &l, int const &n) {
	return l % Rational(n);
}
Rational operator%(int const &n, Rational const &r) {
	return Rational(n) % r;
}
bool operator==(Rational const &l, Rational const &r) {
	return l.n * r.d == r.n * l.d;
}
bool operator==(Rational const &l, int const &n) {
	return l.n == n * l.d;
}
bool operator==(int const &n, Rational const &r) {
	return n * r.d == r.n;
}
auto operator<=>(Rational const &l, Rational const &r) {
	return l.n * r.d <=> r.n * l.d;
}
auto operator<=>(Rational const &l, int const &n) {
	return l.n <=> n * l.d;
}
auto operator<=>(int const &n, Rational const &r) {
	return n * r.d <=> r.n;
}
template <typename T>
Rational &operator+=(Rational &l, T const &x) {
	return l = l + x;
}
template <typename T>
Rational &operator-=(Rational &l, T const &x) {
	return l = l - x;
}
template <typename T>
Rational &operator*=(Rational &l, T const &x) {
	return l = l * x;
}
template <typename T>
Rational &operator/=(Rational &l, T const &x) {
	return l = l / x;
}
template <typename T>
Rational &operator%=(Rational &l, T const &x) {
	return l = l % x;
}
