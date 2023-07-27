#include <math.h>
#include <fstream>
#include <iostream>
#include <stack>
#include <string>
#include <utility>
#include <vector>
#include "rational.hpp"
#if defined _WIN32
#include <Windows.h>
#elif defined __unix__
#include <unistd.h>
#endif
#define TAU 6.28318530718
#define REC_ERR 1
#define REC_TXT 2
#define REC_WAV 4
#define REC_TIM 8
#define BITS_T char
#define BITS_M 127
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
    WavHead(uint32_t ds):
        data_size(ds),
        fmat_size(sizeof fmat),
        riff_size(sizeof wave_ID + sizeof fmat_ID + sizeof fmat_size + sizeof fmat + sizeof data_ID + sizeof data_size + ds) {}
};
struct Tone {
    double freq, dura = 0;
    std::vector<BITS_T> wave(char t) const {
        int size = dura * WAV_SR;
        int peri = WAV_SR / freq;
        std::vector<BITS_T> wave(size, BITS_M);
        for (int i = 0; i < size; i++) {
            wave[i] += fmin(1.0, fmin(i, size - i) / (0.02 * WAV_SR)) * BITS_M * (
                not freq ? 0.0 :
                t == '1' ? i % peri < peri / 2 ? -1.0 : 1.0 : // square
                t == '2' ? (double)(abs(i % peri * 4 - peri * 2) - peri) / peri : // triangle
                t == '3' ? (double)(abs(i % peri * 2 - peri * 0) - peri) / peri : // sawtooth
                t == '4' ? sin(TAU / WAV_SR * freq * i) * 0.6 - sin(TAU / WAV_SR * (freq + 5) * i) * 0.4 : // beat
                           sin(TAU / WAV_SR * freq * i) * 1.0 - sin(TAU / WAV_SR * (freq + 5) * i) * 0.0); // sine
        }
        return wave;
    }
};
class Passage {
    struct Note {
        Rational value;
        int solfa, accidental, octave = 0;
    };
    struct Warn {
        int mctr;
        Rational mval;
    };
    std::vector<Note> notes;
    std::vector<Warn> warns;
    std::string const mode;
    std::pair<int, int> const metr;
    int const bpm;
public:
    Passage(std::string const &md, std::pair<int, int> const &mt, int tm, std::ifstream &input):
        mode(md), metr(mt), bpm(tm) {
        Rational crotchet(1, 4);
        std::stack<Rational> tuplets;
        for (int mctr = 1, c; c = input.peek(), c != '&' && c != '|' && c != ':'; mctr++) {
            int persist[7] = {0};
            std::vector<Note> measure;
            for (int as, bs, c; c = input.get(), c != '|';) {
                switch (c) {
                case '1': case '2': case '3': case '4': case '5': case '6': case '7':
                    measure.push_back({crotchet, c, persist[c - '1']});
                    break;
                case ',': case '0':
                    measure.push_back({crotchet, c, 0});
                    break;
                case '=':
                    measure.back().accidental = persist[measure.back().solfa - '1'] = 0;
                    break;
                case '#':
                    measure.back().accidental = persist[measure.back().solfa - '1'] = 1;
                    break;
                case 'b':
                    measure.back().accidental = persist[measure.back().solfa - '1'] = -1;
                    break;
                case '^':
                    measure.back().octave++;
                    break;
                case 'v':
                    measure.back().octave--;
                    break;
                case '-':
                    measure.back().value += crotchet;
                    break;
                case '/':
                    measure.back().value /= 2;
                    break;
                case '.':
                    measure.back().value *= Rational(1, 2 * (measure.back().value / crotchet).numerator()) + 1;
                    break;
                case '<':
                    crotchet /= 2;
                    break;
                case '>':
                    crotchet *= 2;
                    break;
                case '[':
                    input >> as;
                    input.get(); // ':'
                    input >> bs;
                    input.get(); // ']'
                    tuplets.emplace(as, bs);
                    crotchet /= tuplets.top();
                    break;
                case '!':
                    crotchet *= tuplets.top();
                    tuplets.pop();
                    break;
                }
            }
            Rational mval;
            for (auto const &n : measure) {
                mval += n.value;
            }
            if (mval != Rational(metr.first, metr.second)) {
                warns.push_back({mctr, mval});
            }
            notes.insert(notes.end(), measure.begin(), measure.end());
        }
    }
    void pshow(int i = 0) const {
        std::cerr << color_info << "Passage " << i << ": " << color_end
                  << "mode = " << mode << ", "
                  << "metr = " << metr.first << "/" << metr.second << ", "
                  << "speed = " << bpm << " bpm, "
                  << "notes = " << notes.size() << "." << std::endl;
        for (auto const &warn : warns) {
            std::cerr << color_warn << "Warn: " << color_end
                      << "the " << std::to_string(warn.mctr)
                       + "tsnrtttttt"[(warn.mctr % 100) / 10 == 1 ? 0 : warn.mctr % 10]
                       + "htddhhhhhh"[(warn.mctr % 100) / 10 == 1 ? 0 : warn.mctr % 10] << " measure is irregular. "
                      << "(" << std::to_string(warn.mval.numerator()) << "/" << std::to_string(warn.mval.denominator()) << ")" << std::endl;
        }
    }
    std::vector<Tone> tones() const {
        int const pitch[7] = {0, 2, 4, 5, 7, 9, 11};
        int reference = 3;
        if (mode[0] >= 'A' && mode[0] <= 'G') {
            reference = (pitch[(mode[0] - 'C' + 7) % 7] + 3) % 12 + 0;
        }
        if (mode[0] >= 'a' && mode[0] <= 'g') {
            reference = (pitch[(mode[0] - 'c' + 7) % 7] + 3) % 12 + 3;
        }
        for (auto c : mode.substr(1)) {
            switch (c) {
            case '#':
                reference++;
                break;
            case 'b':
                reference--;
                break;
            case '^':
                reference += 12;
                break;
            case 'v':
                reference -= 12;
                break;
            }
        }
        std::vector<Tone> tones;
        for (auto const &note : notes) {
            if (note.solfa != ',') {
                tones.push_back({note.solfa != '0' ? 440 * pow(2, (reference + pitch[note.solfa - '1'] + note.accidental) / 12.0 + note.octave) : 0.0});
            }
            if (tones.size() != 0) {
                tones.back().dura += (note.value * 60 * metr.second / bpm).value();
            }
        }
        return tones;
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
        for (endchar = '&'; endchar == '&'; endchar = input.get()) {
            if (std::string temp; input >> temp, temp.size() && temp != "~") {
                mode = temp;
                input >> metr.first >> endchar >> metr.second >> bpm;
            }
            passages.emplace_back(mode, metr, bpm, input);
        };
        if (endchar == ':') {
            for (int i; input >> i;) {
                order.push_back(i - 1);
            }
        } else {
            for (int i = 0; i < passages.size(); i++) {
                order.push_back(i);
            }
        }
    }
    void mshow() const {
        for (int i = 0; i < passages.size(); i++) {
            passages[i].pshow(i + 1);
        }
        std::cerr << color_info << "Passage order: " << color_end;
        for (int i = 0; i < order.size() - 1; i++) {
            std::cerr << order[i] + 1 << ", ";
        }
        std::cerr << order.back() + 1 << "." << std::endl;
    }
    void msave(std::ofstream &wav_file, char timbre) const {
        std::vector<Tone> tones;
        for (auto const &iter : order) {
            auto passage_tones = passages[iter].tones();
            tones.insert(tones.end(), passage_tones.begin(), passage_tones.end());
        }
        std::vector<BITS_T> data;
        for (auto const &tone : tones) {
            auto tone_data = tone.wave(timbre);
            data.insert(data.end(), tone_data.begin(), tone_data.end());
        }
        int dsize = data.size() * sizeof(BITS_T);
        WavHead *head = new WavHead(dsize);
        wav_file.write((char *)head, sizeof *head);
        wav_file.write((char *)data.data(), dsize);
        delete head;
    }
};
int main(int argc, char *argv[]) {
    bool color_support = false;
#if defined _WIN32
    HANDLE hStderr = GetStdHandle(STD_ERROR_HANDLE);
    DWORD dwStderrMode;
    BOOL bStderr = GetConsoleMode(hStderr, &dwStderrMode);
    color_support = bStderr && SetConsoleMode(hStderr, dwStderrMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
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
    std::ifstream txt_file;
    std::ofstream wav_file;
    char timbre = '0';
    for (int i = 1; (rec & REC_ERR) == 0 && i < argc; i++) {
        if (argv[i][0] == '-') {
            if (argv[i][1] == 't') {
                if ((rec & REC_TIM) == 0 && ((timbre = argv[i][2]) | 7) == '7' && argv[i][3] == '\0') {
                    rec |= REC_TIM;
                } else {
                    rec |= REC_ERR;
                }
            } else if (argv[i][1] == 'o' && argv[i][2] == '\0') {
                if ((rec & REC_WAV) == 0 && i + 1 < argc && (wav_file.open(argv[++i], std::ios::binary), wav_file.is_open())) {
                    rec |= REC_WAV;
                } else {
                    rec |= REC_ERR;
                }
            } else {
                rec |= REC_ERR;
            }
        } else if ((rec & REC_TXT) == 0 && (txt_file.open(argv[i]), txt_file.is_open())) {
            rec |= REC_TXT;
        } else {
            rec |= REC_ERR;
        }
    }
    if ((rec & REC_ERR) != 0 || (rec & REC_TXT) == 0 || (rec & REC_WAV) == 0 && not(wav_file.open("a.wav", std::ios::binary), wav_file.is_open())) {
        std::cerr << "Description: Generate audio file from numeric music notation." << std::endl
                  << "Usage: " << argv[0] << " [-o OUTFILE] [-t<n>] FILE" << std::endl
                  << "Options:" << std::endl
                  << "  FILE        input file name" << std::endl
                  << "  -o OUTFILE  output file name (default: a.wav)" << std::endl
                  << "  -t0         timbre: sine wave (default)" << std::endl
                  << "  -t1         timbre: square wave" << std::endl
                  << "  -t2         timbre: triangle wave" << std::endl
                  << "  -t3         timbre: sawtooth wave" << std::endl
                  << "  -t4         timbre: superimposed sine waves" << std::endl;
        return 1;
    }
    Music mu(txt_file);
    mu.mshow();
    mu.msave(wav_file, timbre);
#if defined _WIN32
    color_support = bStderr && SetConsoleMode(hStderr, dwStderrMode);
#endif
    return 0;
}
