#include <math.h>
#include <fstream>
#include <iostream>
#include <stack>
#include <string>
#include <vector>
#include "rational.hpp"
#if defined _WIN32
#include <io.h>
#include <windows.h>
#elif defined __unix__
#include <unistd.h>
#endif
#define TAU 6.28318530718
#define REC_FLS 1
#define REC_TXT 2
#define REC_WAV 4
#define REC_TIM 8
#define BITS_T char
#define BITS_M 127
#define WAV_SR 44100
using namespace std;
static string color_log, color_warn, color_err, color_end;
struct WavHead {
	char riff_ID[4] = {'R', 'I', 'F', 'F'};
	uint32_t riff_size;
	char format[4] = {'W', 'A', 'V', 'E'};
	char fmt_ID[4] = {'f', 'm', 't', ' '};
	uint32_t fmt_size;
	struct Format {
		uint16_t audio_format;
		uint16_t channels;
		uint32_t sample_rate;
		uint32_t byte_rate;
		uint16_t block_size;
		uint16_t sample_bits;
	} fmt = {1, 1, WAV_SR, WAV_SR * sizeof(BITS_T), sizeof(BITS_T), 8 * sizeof(BITS_T)};
	char data_ID[4] = {'d', 'a', 't', 'a'};
	uint32_t data_size;
	WavHead(uint32_t const &ds) : data_size(ds), fmt_size(sizeof fmt), riff_size(sizeof format + sizeof fmt_ID + sizeof fmt_size + sizeof fmt + sizeof data_ID + sizeof data_size + ds) {}
};
string ordinal(int const &n) {
	return (n % 100) / 10 == 1 ? to_string(n) + "th" : to_string(n) + "tsnrtttttt"[n % 10] + "htddhhhhhh"[n % 10];
}
struct Tone {
	double frequency, duration;
	Tone(double const &f) : frequency(f), duration(0) {}
	vector<BITS_T> wave(char const &timbre) const {
		int size = duration * WAV_SR;
		int period = WAV_SR / frequency;
		vector<BITS_T> wave(size, BITS_M);
		if (frequency)
			switch (timbre) {
			case '1':
				for (int i = 0; i < size; i++)
					wave[i] += min(1.0, min(i, size - i) / (0.02 * WAV_SR)) * (i % period < period / 2 ? -BITS_M : BITS_M);
				break;
			case '2':
				for (int i = 0; i < size; i++)
					wave[i] += min(1.0, min(i, size - i) / (0.02 * WAV_SR)) * BITS_M * (abs(i % period * 4 - period * 2) - period) / period;
				break;
			case '3':
				for (int i = 0; i < size; i++)
					wave[i] += min(1.0, min(i, size - i) / (0.02 * WAV_SR)) * BITS_M * (i % period * 2 - period) / period;
				break;
			case '4':
				for (int i = 0; i < size; i++)
					wave[i] += min(1.0, min(i, size - i) / (0.02 * WAV_SR)) * BITS_M * (sin(TAU / WAV_SR * frequency * i) * 0.6 - sin(TAU / WAV_SR * (frequency + 5) * i) * 0.4);
				break;
			default:
				for (int i = 0; i < size; i++)
					wave[i] += min(1.0, min(i, size - i) / (0.02 * WAV_SR)) * BITS_M * sin(TAU / WAV_SR * frequency * i);
				break;
			}
		return wave;
	}
};
class Passage {
	static constexpr int pitch[7] = {0, 2, 4, 5, 7, 9, 11};
	string const mode;
	int const metre[2];
	int const bpm;
	struct Note {
		int solfa, accidental, octave;
		Rational value;
		Note(int const &n, int const &a, Rational const &l) : solfa(n), accidental(a), octave(0), value(l) {}
	};
	vector<Note> notes;
	struct Warn {
		int measure;
		Rational mval;
		Warn(int const &m, Rational const &v) : measure(m), mval(v) {}
	};
	vector<Warn> warns;
public:
	Passage(string const &md, int const (&mt)[2], int const &tm, istream &input) : mode(md), metre{mt[0], mt[1]}, bpm(tm) {
		int persist[7] = {};
		Rational crotchet(1, 4);
		stack<Rational> tuplets;
		for (int measure = 0, mcount = 0, c; (c = input.get()) != EOF;)
			if (c >= '1' && c <= '7')
				notes.emplace_back(c - '0', persist[c - '1'], crotchet);
			else if (c == '0')
				notes.emplace_back(0, 0, crotchet);
			else if (c == ',')
				notes.emplace_back(-1, 0, crotchet);
			else
				switch (c) {
				case '#':
					if (notes.back().solfa)
						notes.back().accidental = persist[notes.back().solfa - 1] = 1;
					break;
				case 'b':
					if (notes.back().solfa)
						notes.back().accidental = persist[notes.back().solfa - 1] = -1;
					break;
				case '=':
					if (notes.back().solfa)
						notes.back().accidental = persist[notes.back().solfa - 1] = 0;
					break;
				case '^':
					notes.back().octave++;
					break;
				case 'v':
					notes.back().octave--;
					break;
				case '-':
					notes.back().value += crotchet;
					break;
				case '/':
					notes.back().value /= 2;
					break;
				case '.':
					notes.back().value *= Rational(1, 2 * (notes.back().value / crotchet).numerator()) + 1;
					break;
				case '<':
					crotchet /= 2;
					break;
				case '>':
					crotchet *= 2;
					break;
				case '[': {
					int p;
					input >> p;
					for (tuplets.emplace(p); tuplets.top() / 2 > 1; tuplets.top() /= 2)
						;
					crotchet /= tuplets.top();
					break;
				}
				case ']':
					crotchet *= tuplets.top();
					tuplets.pop();
					break;
				case '|': {
					for (int i = 0; i < 7; i++)
						persist[i] = 0;
					measure++;
					Rational mvalue;
					for (; mcount < notes.size(); mcount++)
						mvalue += notes[mcount].value;
					if (mvalue != Rational(metre[0], metre[1]))
						warns.emplace_back(measure, mvalue);
					switch (input.peek()) {
					case '&':
					case ':':
					case '|':
						return;
					}
				}
				}
	}
	void show() const {
		cerr << color_log << "info: " << color_end << "mode = " << mode << ", metre = " << metre[0] << "/" << metre[1] << ", speed = " << bpm << " bpm, notes = " << notes.size() << "." << endl;
		for (auto const &warn : warns)
			cerr << color_warn << "warning: " << color_end << "the " << ordinal(warn.measure) << " measure is irregular. (" << to_string(warn.mval.numerator()) << "/" << to_string(warn.mval.denominator()) << ")" << endl;
	}
	vector<Tone> get() const {
		int reference = 3;
		if (mode[0] >= 'A' && mode[0] <= 'G')
			reference = (pitch[(mode[0] - 'C' + 7) % 7] + 3) % 12;
		else if (mode[0] >= 'a' && mode[0] <= 'g')
			reference = (pitch[(mode[0] - 'c' + 7) % 7] + 3) % 12 + 3;
		for (auto const &c : mode.substr(1))
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
		vector<Tone> tones;
		for (auto const &note : notes) {
			if (note.solfa != -1)
				tones.emplace_back(note.solfa ? 440 * pow(2, (double)(reference + pitch[note.solfa - 1] + note.accidental) / 12 + note.octave) : 0);
			tones.back().duration += (note.value * 60 * metre[1] / bpm).value();
		}
		return tones;
	}
};
class Music {
	vector<Passage> passages;
	vector<int> order;
public:
	Music(istream &input) {
		char end;
		string mode = "C";
		int metre[2] = {4, 4};
		int bpm = 88;
		do {
			if (string temp; input >> temp, temp.size() && temp != "~")
				mode = temp, input >> metre[0] >> end >> metre[1] >> bpm;
			passages.emplace_back(mode, metre, bpm, input);
		} while ((end = input.get()) == '&');
		if (end == ':')
			for (int i; input >> i;)
				order.push_back(i - 1);
		else
			for (int i = 0; i < passages.size(); i++)
				order.push_back(i);
	}
	void show() const {
		for (auto const &passage : passages)
			passage.show();
		cerr << color_log << "order: " << color_end;
		for (int i = 0; i < order.size() - 1; i++)
			cerr << order[i] + 1 << ", ";
		cerr << order.back() + 1 << "." << endl;
	}
	void save(ofstream &wav_file, char const &timbre) const {
		vector<Tone> tones;
		for (auto const &i : order) {
			auto passage_tones = passages[i].get();
			tones.insert(tones.end(), passage_tones.begin(), passage_tones.end());
		}
		vector<BITS_T> data;
		for (auto const &tone : tones) {
			auto tone_data = tone.wave(timbre);
			data.insert(data.end(), tone_data.begin(), tone_data.end());
		}
		int sizeof_data = data.size() * sizeof(BITS_T);
		WavHead head(sizeof_data);
		wav_file.write((char *)&head, sizeof head);
		wav_file.write((char *)&data[0], sizeof_data);
	}
};
int main(int argc, char *argv[]) {
	bool color_support = false;
#if defined _WIN32
	HANDLE hStderr = GetStdHandle(STD_ERROR_HANDLE);
	DWORD dwStderrMode;
	BOOL bStderr = GetConsoleMode(hStderr, &dwStderrMode);
	if (bStderr)
		color_support = SetConsoleMode(hStderr, dwStderrMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);
#elif defined __unix__
	color_support = isatty(fileno(stderr));
#endif
	if (color_support) {
		color_log = "\033[32m";
		color_warn = "\033[33m";
		color_err = "\033[31m";
		color_end = "\033[0m";
	}
	int rec = 0;
	ifstream txt_file;
	ofstream wav_file;
	char timbre = '0';
	for (int i = 1; (rec & REC_FLS) == 0 and i < argc; i++)
		if (argv[i][0] == '-')
			if (argv[i][1] == 't')
				if ((rec & REC_TIM) == 0 and ((timbre = argv[i][2]) | 7) == '7' and argv[i][3] == '\0')
					rec |= REC_TIM;
				else
					rec |= REC_FLS;
			else if (argv[i][1] == 'o' and argv[i][2] == '\0')
				if ((rec & REC_WAV) == 0 and i + 1 < argc and (wav_file.open(argv[++i], ios::binary), wav_file.is_open()))
					rec |= REC_WAV;
				else
					rec |= REC_FLS;
			else
				rec |= REC_FLS;
		else if ((rec & REC_TXT) == 0 and (txt_file.open(argv[i]), txt_file.is_open()))
			rec |= REC_TXT;
		else
			rec |= REC_FLS;
	if ((rec & REC_FLS) != 0) {
		cerr << color_err << "usage: " << color_end << argv[0] << " [NMN] [-o WAV] [-tN]" << endl;
		return 1;
	}
	if ((rec & REC_WAV) == 0)
		wav_file.open("a.wav", ios::binary);
	Music mu((rec & REC_TXT) == 0 ? cin : txt_file);
	mu.show();
	mu.save(wav_file, timbre);
#if defined _WIN32
	if (bStderr)
		color_support = SetConsoleMode(hStderr, dwStderrMode);
#endif
}
