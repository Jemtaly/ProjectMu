#pragma once
#include <compare>
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
    Rational(int numerator = 0, int denominator = 1) {
        if (denominator < 0) {
            n = -numerator;
            d = -denominator;
        } else {
            n = numerator;
            d = denominator;
        }
        reduce();
    }
    auto numerator() const {
        return n;
    }
    auto denominator() const {
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
    friend Rational operator+(Rational const &r) {
        return Rational(r.n, r.d);
    }
    friend Rational operator-(Rational const &r) {
        return Rational(-r.n, r.d);
    }
    friend Rational operator~(Rational const &r) {
        return Rational(r.d, r.n);
    }
    friend Rational operator+(Rational const &l, Rational const &r) {
        return Rational(l.n * r.d + r.n * l.d, l.d * r.d);
    }
    friend Rational operator+(Rational const &l, int n) {
        return Rational(l.n + l.d * n, l.d);
    }
    friend Rational operator+(int n, Rational const &r) {
        return Rational(r.n + r.d * n, r.d);
    }
    friend Rational operator-(Rational const &l, Rational const &r) {
        return Rational(l.n * r.d - r.n * l.d, l.d * r.d);
    }
    friend Rational operator-(Rational const &l, int n) {
        return Rational(l.n - l.d * n, l.d);
    }
    friend Rational operator-(int n, Rational const &r) {
        return Rational(r.d * n - r.n, r.d);
    }
    friend Rational operator*(Rational const &l, Rational const &r) {
        return Rational(l.n * r.n, l.d * r.d);
    }
    friend Rational operator*(Rational const &l, int n) {
        return Rational(l.n * n, l.d);
    }
    friend Rational operator*(int n, Rational const &r) {
        return Rational(r.n * n, r.d);
    }
    friend Rational operator/(Rational const &l, Rational const &r) {
        return Rational(l.n * r.d, r.n * l.d);
    }
    friend Rational operator/(Rational const &l, int n) {
        return Rational(l.n, l.d * n);
    }
    friend Rational operator/(int n, Rational const &r) {
        return Rational(r.d * n, r.n);
    }
    friend Rational operator%(Rational const &l, Rational const &r) {
        return l - (l / r).floor() * r;
    }
    friend Rational operator%(Rational const &l, int n) {
        return l % Rational(n);
    }
    friend Rational operator%(int n, Rational const &r) {
        return Rational(n) % r;
    }
    friend bool operator==(Rational const &l, Rational const &r) {
        return l.n * r.d == r.n * l.d;
    }
    friend bool operator==(Rational const &l, int n) {
        return l.n == n * l.d;
    }
    friend bool operator==(int n, Rational const &r) {
        return n * r.d == r.n;
    }
    friend auto operator<=>(Rational const &l, Rational const &r) {
        return l.n * r.d <=> r.n * l.d;
    }
    friend auto operator<=>(Rational const &l, int n) {
        return l.n <=> n * l.d;
    }
    friend auto operator<=>(int n, Rational const &r) {
        return n * r.d <=> r.n;
    }
    template <typename T>
    Rational &operator+=(T const &r) {
        return *this = *this + r;
    }
    template <typename T>
    Rational &operator-=(T const &r) {
        return *this = *this - r;
    }
    template <typename T>
    Rational &operator*=(T const &r) {
        return *this = *this * r;
    }
    template <typename T>
    Rational &operator/=(T const &r) {
        return *this = *this / r;
    }
    template <typename T>
    Rational &operator%=(T const &r) {
        return *this = *this % r;
    }
};
