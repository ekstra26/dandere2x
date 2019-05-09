#include "Driver.h"

/**
 * Todo
 * - Implement CLI interface into dandere2x python for long -term usability.
 * - Debug function for people to test individual features
 */

/**
 * Known Bugs
 */

#include <ctime>

int main(int argc, char **argv) {
    bool debug = false; //debug flag

    string workspace = "C:\\Users\\windwoz\\Desktop\\workspace\\shelter_mse\\";
    int frame_count = 130;
    int block_size = 30;
    double tolerance = 15;
    int step_size = 4;
    string run_type = "n";// 'n' or 'r'
    int resume_frame = 23;
    string extension_type = ".jpg";

    cout << "hello world!" << endl;

    if (!debug) {
        workspace = argv[1];
        frame_count = atoi(argv[2]);
        block_size = atoi(argv[3]);
        tolerance = stod(argv[4]);
        step_size = stod(argv[5]);
        run_type = argv[6];
        resume_frame = atoi(argv[7]);
        extension_type = argv[8];

    }

    cout << "Settings" << endl;
    cout << "workspace: " << workspace << endl;
    cout << "frame_count: " << frame_count << endl;
    cout << "block_size: " << block_size << endl;
    cout << "tolerance: " << tolerance << endl;
    cout << "step_size: " << step_size << endl;
    cout << "run_type: " << run_type << endl;
    cout << "ResumeFrame (if valid): " << resume_frame << endl;
    cout << "extension_type: " << extension_type << endl;

    if (run_type == "n") {
        driver_difference(workspace, 1, frame_count, block_size, tolerance, step_size, extension_type);
    } else if (run_type == "r") {
        driver_difference(workspace, resume_frame, frame_count, block_size, tolerance, step_size, extension_type);
    }
    return 0;
}
