#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stack>
#include <string>
#include <utility>
#include <vector>
#include "rational.hpp"
#if defined _WIN32
#include <Windows.h>
#undef min
#undef max
#elif defined __unix__
#include <unistd.h>
#endif
#define TAU 6.28318530718
#define REC_ERR 1
#define REC_TXT 2
#define REC_WAV 4
#define REC_TIM 8
#define BITS_T int16_t // uint8_t, int16_t, int32_t, int64_t
#define WAV_SR 44100
static std::string color_info, color_warn, color_err, color_end;
struct WavHead {
    char riff_ID[4] = {'R', 'I', 'F', 'F'};
    uint32_t riff_size;
    char wave_ID[4] = {'W', 'A', 'V', 'E'};
    char fmat_ID[4] = {'f', 'm', 't', ' '};
    uint32_t fmat_size;
    struct Format {
        uint16_t audio_format;
        uint16_t channels;
        uint32_t sample_rate;
        uint32_t byte_rate;
        uint16_t block_size;
        uint16_t sample_bits;
    } fmat = {1, 1, WAV_SR, WAV_SR * sizeof(BITS_T), sizeof(BITS_T), 8 * sizeof(BITS_T)};
    char data_ID[4] = {'d', 'a', 't', 'a'};
    uint32_t data_size;
    WavHead(uint32_t ds_in_bytes):
        data_size(ds_in_bytes),
        fmat_size(sizeof fmat),
        riff_size(sizeof wave_ID + sizeof fmat_ID + sizeof fmat_size + sizeof fmat + sizeof data_ID + sizeof data_size + ds_in_bytes) {}
};
struct Tone {
    double freq, dura = 0.0;
    void generate(std::back_insert_iterator<std::vector<BITS_T>> dest, char t) const {
        int size = round(WAV_SR * dura + 0.0);
        int perr = round(WAV_SR / freq + 0.0);
        int perx = round(WAV_SR / freq + 0.5);
        double F = freq / WAV_SR;
        double A = TAU / WAV_SR * (freq + 0.0);
        double B = TAU / WAV_SR * (freq + 5.0);
        std::vector<double> wave(size);
        for (int i = 0; i < size; i++) {
            wave[i] = not freq ? 0.0
                    : t == '0' ? sin(A * i) * 1.0 - sin(B * i) * 0.0 // sine
                    : t == '1' ? sin(A * i) * 0.6 - sin(B * i) * 0.4 // superimposed sine
                    : t == '2' ? fabs(fmod(F * i, 1.0) * 4.0 - 2.0) - 1.0 // triangle
                    : t == '3' ? fabs(fmod(F * i, 1.0) * 2.0 - 0.0) - 1.0 // sawtooth
                    : t == '4' ? i % perr < perr / 2 ? -1.0 : 1.0 // square
                    : i < perx ? rand() / (double)RAND_MAX * 2.0 - 1.0 : (wave[i - perx] + wave[i - perx + 1]) * 0.5; // karplus-strong
        }
        for (int i = 0; i < size; i++) {
            wave[i] = wave[i] * fmin(1.0, fmin(i, size - i) / (0.02 * WAV_SR)); // fade in & out (0.02s)
        }
        std::transform(wave.begin(), wave.end(), dest, [](double x) -> BITS_T {
            constexpr double mm = std::numeric_limits<BITS_T>::max() - std::numeric_limits<BITS_T>::min() + 1;
            constexpr double lo = std::numeric_limits<BITS_T>::min();
            constexpr double hi = std::numeric_limits<BITS_T>::max();
            return x >= 1.0 ? hi : x < -1.0 ? lo : floor((x + 1.0) * 0.5 * mm + lo);
        });
    }
};
class Passage {
    static constexpr int pitch[7] = {0, 2, 4, 5, 7, 9, 11};
    struct Note {
        Rational value;
        int solfa, accidental, octave = 0;
    };
    std::vector<Note> notes;
    std::pair<int, int> const metr;
    int const bpm;
    int reference;
public:
    Passage(std::string const &mode, std::pair<int, int> const &metr, int bpm, std::ifstream &input):
        metr(metr), bpm(bpm), reference(3) {
        for (auto c : mode) {
            switch (c) {
            case 'C': case 'D': case 'E': case 'F': case 'G': case 'A': case 'B':
                reference = (pitch[(c - 'C' + 7) % 7] + 3) % 12; break;
            case '#':
                reference++; break;
            case 'b':
                reference--; break;
            case '^':
                reference += 12; break;
            case 'v':
                reference -= 12; break;
            }
        }
        Rational crotchet(1, 4);
        std::stack<Rational> tuplets;
        for (int mctr = 1, c; c = input.peek(), c != '&' && c != '|' && c != ':' && c != '~'; mctr++) {
            int persist[7] = {};
            std::vector<Note> measure;
            for (int as, bs, c; c = input.get(), c != '|';) {
                switch (c) {
                case '1': case '2': case '3': case '4': case '5': case '6': case '7':
                    measure.push_back({crotchet, c, persist[c - '1']});
                    break;
                case ',': case '0':
                    measure.push_back({crotchet, c, 0}); break;
                case '=':
                    if (measure.empty()) {
                        throw std::runtime_error("'=' shouldn't appear at the beginning of a measure.");
                    }
                    measure.back().accidental = persist[measure.back().solfa - '1'] = 0; break;
                case '#':
                    if (measure.empty()) {
                        throw std::runtime_error("'#' shouldn't appear at the beginning of a measure.");
                    }
                    measure.back().accidental = persist[measure.back().solfa - '1'] = 1; break;
                case 'b':
                    if (measure.empty()) {
                        throw std::runtime_error("'b' shouldn't appear at the beginning of a measure.");
                    }
                    measure.back().accidental = persist[measure.back().solfa - '1'] = -1; break;
                case '^':
                    if (measure.empty()) {
                        throw std::runtime_error("'^' shouldn't appear at the beginning of a measure.");
                    }
                    measure.back().octave++; break;
                case 'v':
                    if (measure.empty()) {
                        throw std::runtime_error("'v' shouldn't appear at the beginning of a measure.");
                    }
                    measure.back().octave--; break;
                case '-':
                    if (measure.empty()) {
                        throw std::runtime_error("'-' shouldn't appear at the beginning of a measure, use ',' instead.");
                    }
                    measure.back().value += crotchet; break;
                case '/':
                    if (measure.empty()) {
                        throw std::runtime_error("'/' shouldn't appear at the beginning of a measure.");
                    }
                    measure.back().value /= 2; break;
                case '.':
                    if (measure.empty()) {
                        throw std::runtime_error("'.' shouldn't appear at the beginning of a measure.");
                    }
                    measure.back().value *= Rational(1, 2 * (measure.back().value / crotchet).numerator()) + 1; break;
                case '<':
                    crotchet /= 2; break;
                case '>':
                    crotchet *= 2; break;
                case '[':
                    input >> as;
                    input.get();  // ':'
                    input >> bs;
                    input.get();  // ']'
                    tuplets.emplace(as, bs);
                    crotchet /= tuplets.top();
                    break;
                case '!':
                    if (tuplets.empty()) {
                        throw std::runtime_error("shouldn't close a tuplet that hasn't been opened.");
                    }
                    crotchet *= tuplets.top();
                    tuplets.pop(); break;
                case EOF:
                    throw std::runtime_error("unexpected end of file.");
                }
            }
            Rational mval;
            for (auto const &n : measure) {
                mval += n.value;
            }
            if (mval != Rational(metr.first, metr.second)) {
                std::cerr << color_warn << "Warn: " << color_end
                          << "the " << std::to_string(mctr) + "tsnrtttttt"[(mctr % 100) / 10 == 1 ? 0 : mctr % 10] + "htddhhhhhh"[(mctr % 100) / 10 == 1 ? 0 : mctr % 10] << " measure is irregular. "
                          << "(" << std::to_string(mval.numerator()) << "/" << std::to_string(mval.denominator()) << ")" << std::endl;
            }
            notes.insert(notes.end(), measure.begin(), measure.end());
        }
    }
    void join(std::vector<Tone> &tones) const {
        for (auto const &note : notes) {
            if (note.solfa != ',') {
                tones.push_back({note.solfa != '0' ? 440 * pow(2, (reference + pitch[note.solfa - '1'] + note.accidental) / 12.0 + note.octave) : 0.0});
            }
            tones.back().dura += (note.value * 60 * metr.second / bpm).value();
        }
    }
};
class Music {
    std::vector<Passage> passages;
    std::vector<int> order;
public:
    Music(std::ifstream &input) {
        std::string mode = "C";
        std::pair<int, int> metr = {4, 4};
        int bpm = 88;
        char endchar;
        for (endchar = '&'; endchar == '&' || endchar == '~'; endchar = input.get()) {
            if (endchar == '&') {
                input >> mode >> metr.first >> endchar >> metr.second >> bpm;
            }
            std::cerr << color_info << "Passage " << passages.size() + 1 << ": " << color_end
                      << "mode = " << mode << ", "
                      << "metr = " << metr.first << "/" << metr.second << ", "
                      << "speed = " << bpm << " bpm." << std::endl;
            passages.emplace_back(mode, metr, bpm, input);
        }
        if (endchar == ':') {
            for (int i; input >> i;) {
                if (i < 1 || i > passages.size()) {
                    throw std::runtime_error("passage index out of range: " + std::to_string(i));
                }
                order.push_back(i - 1);
            }
        } else {
            for (int i = 0; i < passages.size(); i++) {
                order.push_back(i);
            }
        }
        std::cerr << color_info << "Passage order: " << color_end;
        for (int i = 0; i < order.size() - 1; i++) {
            std::cerr << order[i] + 1 << ", ";
        }
        std::cerr << order.back() + 1 << "." << std::endl;
    }
    void save(std::ofstream &wav_file, char timbre) const {
        std::vector<Tone> tones = {{0.0}};
        for (auto iter : order) {
            passages[iter].join(tones);
        }
        std::vector<BITS_T> data;
        for (auto const &tone : tones) {
            tone.generate(std::back_inserter(data), timbre);
        }
        uint32_t bytes = data.size() * sizeof(BITS_T);
        WavHead const head(bytes);
        wav_file.write((char const *)&head, sizeof head);
        wav_file.write((char const *)data.data(), bytes);
    }
};
int main(int argc, char *argv[]) {
    bool color_support = false;
#if defined _WIN32
    HANDLE hStderr = GetStdHandle(STD_ERROR_HANDLE);
    DWORD dwStderrMode;
    color_support = GetConsoleMode(hStderr, &dwStderrMode) && SetConsoleMode(hStderr, dwStderrMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
#elif defined __unix__
    color_support = isatty(fileno(stderr));
#endif
    if (color_support) {
        color_info = "\033[32m";
        color_warn = "\033[33m";
        color_err = "\033[31m";
        color_end = "\033[0m";
    }
    int rec = 0;
    char timbre = '0';
    std::string txt_name = "-";
    std::string wav_name = "a.wav";
    for (int i = 1; (rec & REC_ERR) == 0 && i < argc; i++) {
        if (argv[i][0] == '-') {
            if (argv[i][1] == 't') {
                if ((rec & REC_TIM) == 0 && ((timbre = argv[i][2]) | 7) == '7' && argv[i][3] == '\0') {
                    rec |= REC_TIM;
                } else {
                    rec |= REC_ERR;
                }
            } else if (argv[i][1] == 'o' && argv[i][2] == '\0') {
                if ((rec & REC_WAV) == 0 && i + 1 < argc) {
                    wav_name = argv[++i];
                    rec |= REC_WAV;
                } else {
                    rec |= REC_ERR;
                }
            } else {
                rec |= REC_ERR;
            }
        } else if ((rec & REC_TXT) == 0) {
            txt_name = argv[i];
            rec |= REC_TXT;
        } else {
            rec |= REC_ERR;
        }
    }
    if ((rec & REC_ERR) != 0 || (rec & REC_TXT) == 0) {
        std::cerr << "Description: Generate audio file from numeric music notation." << std::endl
                  << "Usage: " << argv[0] << " [-o OUTFILE] [-t<n>] FILE" << std::endl
                  << "Options:" << std::endl
                  << "  FILE        input file name" << std::endl
                  << "  -o OUTFILE  output file name (default: a.wav)" << std::endl
                  << "  -t0         timbre: sine wave (default)" << std::endl
                  << "  -t1         timbre: superimposed sine waves" << std::endl
                  << "  -t2         timbre: triangle wave" << std::endl
                  << "  -t3         timbre: sawtooth wave" << std::endl
                  << "  -t4         timbre: square wave" << std::endl
                  << "  -t5         timbre: plucked string" << std::endl;
        return 1;
    }
    try {
        std::ifstream txt_file = std::ifstream(txt_name);
        if (not txt_file.is_open()) {
            throw std::runtime_error("cannot open the input file: " + txt_name);
        }
        Music mu(txt_file);
        std::ofstream wav_file = std::ofstream(wav_name, std::ios::binary);
        if (not wav_file.is_open()) {
            throw std::runtime_error("cannot open the output file: " + wav_name);
        }
        mu.save(wav_file, timbre);
    } catch (std::exception const &e) {
        std::cerr << color_err << "Error: " << color_end << e.what() << std::endl;
        return 1;
    }
    return 0;
}
