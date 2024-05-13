# Focal Plane Mask Control Procedure

## Overview
The Focal Plane Mask Control Procedure is a mini project developed by the EvWaCo Prototype team at Narit. Its primary objective is to integrate the control of a nano-piezo actuator to the measured Full Width at Half Maximum (FWHM) of a mask. The project involves the creation of an application with full access to the actuator. The electronic components utilized include a GigE camera from Point Grey and an actuator from Newport. The ultimate aim is to achieve FWHM adjustment through closed-loop control.

## Objectives
- Integrate control of a nano-piezo actuator with measured mask FWHM.
- Develop an application with complete access to the actuator.
- Utilize a GigE camera from Point Grey and an actuator from Newport.
- Implement closed-loop control to adjust the FWHM.

## Components
- 1 GigE camera from Point Grey.
- 1 actuator from Newport.

## Project Structure
- **Documentation**: Contains project documentation and manuals.
- **Source Code**: Holds the application source code and scripts.
- **Datasheets**: Includes datasheets for electronic components used.
- **Tests**: Stores test scripts and results.

## Usage
1. **Setup**: Install necessary drivers for the camera and actuator.
2. **Calibration**: Calibrate the camera and actuator for accurate measurements.
3. **Integration**: Integrate the camera and actuator control into the application.
4. **Testing**: Test the application's functionality with sample masks.
5. **Optimization**: Fine-tune closed-loop control parameters for optimal performance.

## Requirements
- Python 3.x
- GigE camera driver
- Nano-piezo actuator driver
- Development environment (IDE)
- Necessary libraries and dependencies

## Clone the repository
```bash
git clone https://github.com/Cheer3142/NanoPZ-Focal-Plane-Mask-Ctrl
```

## Acknowledgments
This project was developed as part of the EvWaCo Prototype team's initiatives at Narit.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
