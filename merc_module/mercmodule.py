import numpy
import os
from random import random, sample
from math import sqrt, pi, sin, cos


### Constants
G = 6.674e-8       # cm^3/g/s^2
mSun = 1.99e33     # g
AU = 1.496e13      # cm/AU
day = 24. * 3600.  # s/day


class MercModule:

    FILE_CONTENTS_PLANET_FIRST_LINES = [
        "Mercury   5.427  1.660E-07\n",
        "Venus     5.204  2.4476E-06\n",
        "Earth     5.515  3.0032E-06\n",
        "Mars      3.9335  3.2268E-07\n",
        "Jupiter   1.326  9.54266E-04\n",
        "Io        3.530  4.491E-08\n",
        "Europa    2.99   2.412E-08\n",
        "Ganymede  1.94   7.451E-08\n",
        "Callisto  1.851  5.409E-08\n",
        "Saturn    0.687  2.85717E-04\n",
        "Enceladus 1.606  5.4321E-11\n",
        "Rhea      1.233  1.161E-09\n",
        "Titan     1.880  6.76452E-08\n",
        "Iapetus   1.088  9.0790E-10\n",
        "Uranus    1.318  4.36430E-05\n",
        "Neptune   1.638  5.1486E-05\n",
        "Plantsml    2.0  1.0012066e-17\n"
    ]

    FILE_CONTENTS_SMALL_HEADER = [
        ")O+_06 Small-body initial data  (WARNING: Do not delete this line!!)\n",
        ") Lines beginning with `)' are ignored.\n",
        ")---------------------------------------------------------------------\n",
        "style (Cartesian, Asteroidal, Cometary) = Cartesian\n",
        ")---------------------------------------------------------------------\n",
    ]

    FILE_CONTENTS_BIG_HEADER = [
        ")O+_06 Big-body initial data  (WARNING: Do not delete this line!!)\n",
        ") Lines beginning with `)' are ignored.\n",
        ")---------------------------------------------------------------------\n",
        "style (Cartesian, Asteroidal, Cometary) = Cartesian\n",
        "epoch (in days) = 0.0\n",
        ")---------------------------------------------------------------------\n"
    ]

    @staticmethod
    def FileLength(filename: str) -> int:
        """
        Function to count the number of lines in a file
        """
        with open(filename, "r") as f:
            return sum(1 for _ in f)

    @staticmethod
    def WriteObjInFile(
        current_dir: str,
        subdirectory: str,
        names: list,
        filename: str,
        Header: list,
        FirstLines: list,
        xv,
        s
    ):
        """
        Write big.in or small.in file
        """
        with open(current_dir + '/' + subdirectory + '/In/' + filename + '.in', 'w') as infile:

            # Header
            infile.writelines(Header)
            # Data
            for i in range(len(names)):
                infile.write(FirstLines[i])
                infile.write("  " + xv[i][0] + "  " + xv[i][1] + "  " + xv[i][2] + "\n")
                infile.write("  " + xv[i][3] + "  " + xv[i][4] + "  " + xv[i][5] + "\n")
                infile.write(s[i])

    @staticmethod
    def ReadInfo(whichdir):
        """
        Read info.out, put data into name/destination/time vectors and return
        """
        assert type(whichdir) is str

        here = os.getcwd()

        InfoFile = open(f"{here}/{whichdir}/Out/info.out", 'r')
        InfoLen = MercModule.FileLength(f"{here}/{whichdir}/Out/info.out")
        skip = []
        flen = 7
        header = True
        footer = False
        j = 0

        # Read through the file until reaching the start of integration
        while header:  # header, not needed
            j = j + 1
            line = InfoFile.readline()
            if line == "   Beginning the main integration.\n":
                header = False
                j = j + 1
                line = InfoFile.readline()
        hlen = j + 1
        name1 = [''] * (InfoLen - hlen - flen)
        dest1 = [''] * (InfoLen - hlen - flen)
        time1 = [0] * (InfoLen - hlen - flen)

        # Read through the integration data until reaching the file footer,
        # parsing each line based on # of words to get collision data.
        while not footer:  # body of file
            j = j + 1
            line = InfoFile.readline()
            if line == "   Integration complete.\n":
                footer = True
                break
            splitline = line.split()
            if len(splitline) == 8 and splitline[0] != 'Continuing':
                name1[j - hlen], dest1[j - hlen], time1[j - hlen] = splitline[4], splitline[0], splitline[6]
            elif len(splitline) == 9:
                name1[j - hlen], dest1[j - hlen], time1[j - hlen] = splitline[0], 'Sun', splitline[7]
            elif len(splitline) == 5 and splitline[0] != 'Fractional':
                name1[j - hlen], dest1[j - hlen], time1[j - hlen] = splitline[0], 'Ejected', splitline[3]
            else:
                skip.append(splitline)

        InfoFile.close()
        return name1, dest1, time1

    @staticmethod
    def CopyInfo(whichdir, whichtime, writegood):
        """
        A program to read the collision info from info.out and add it to a running total
        """
        assert type(whichdir) is str
        assert type(whichtime) is str
        assert type(writegood) is bool

        print('CopyInfo ' + whichdir + '/Out/info.out, ' + whichtime)

        # Get collision info from info.out
        name1, dest1, time1 = MercModule.ReadInfo(whichdir)

        # Summarize impacts for infosum.out
        destname = ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Moon', 'Saturn', 'Ejected']
        InfoSum = [0] * len(destname)
        if len(dest1) and any(i != 0 for i in dest1):
            for k, _ in enumerate(destname):
                InfoSum[k] = dest1.count(destname[k])

        # Get which timestep was used, and store in last column of InfoSum
        timestepfile = open(whichdir + '/timestep.txt', 'r')
        timestep = int(timestepfile.readline())
        timestepfile.close()

        # Get total number of objects in simulation
        NUMBER_OF_LINES_IN_OBJECT_GROUPS = 4
        SmallInFileLength = MercModule.FileLength(whichdir + '/In/small.in')
        total_objects_in_file = (SmallInFileLength -
                                 len(MercModule.FILE_CONTENTS_SMALL_HEADER)
            ) / NUMBER_OF_LINES_IN_OBJECT_GROUPS
        NTot = int(total_objects_in_file)
        assert total_objects_in_file == int(NTot)

        # Write summed impacts to file
        InfoSumFile = open(whichdir + '/infosum.out', 'a')
        if os.path.getsize(whichdir + '/infosum.out') == 0:
            InfoSumFile.write('  Su  Me  Ve  Ea  Ma  Ju  Mn  Sa  Ej  Tot Step\n')
        InfoSumFile.write(' {0:3d} {1:3d} {2:3d} {3:3d} {4:3d} {5:3d} {6:3d} {7:3d} {8:3d} {9:4d} {10:4d}\n'.format(
            InfoSum[0], InfoSum[1], InfoSum[2], InfoSum[3], InfoSum[4], InfoSum[5], InfoSum[6], InfoSum[7], InfoSum[8], NTot, timestep)
        )
        InfoSumFile.close()

        # Get .in data for rocks that hit something and write to file
        if writegood:
            gooddest = ['Jupiter', 'Io', 'Europa', 'Ganymede', 'Callisto', 'Moon', 'Saturn', 'Enceladu', 'Rhea', 'Titan', 'Iapetus']
            ind = numpy.array([
                (any(dest1[i] == gooddest[j] for j, _ in enumerate(gooddest)))
                for i, _ in enumerate(dest1)])
            if len(name1) > 0:
                name = numpy.array(name1)[ind]
                goodin = open(whichdir + '/good.in', 'a')
                smallin = open(whichdir + '/In/small.in', 'r')
                SmallLen = MercModule.FileLength(whichdir + '/In/small.in')
                smalllines = ['' for i in range(SmallLen)]
                for j in range(5):
                    smalllines[j] = smallin.readline()
                for j in range(5, SmallLen):
                    smalllines[j] = smallin.readline()
                    if any(name[i] == smalllines[k].split()[0] and float(time1[i]) > 60. for i, _ in enumerate(name) for k in range(j - 3, j + 1)):
                        goodin.write(smalllines[j])
                goodin.close()
                smallin.close()

    @staticmethod
    def MakeMoon(whichdir, whichtime):
        """
        Select a timestep for the big objects and make a new big.in
        """
        assert type(whichdir) is str
        assert type(whichtime) is str
        assert int(whichtime) >= 5

        here = os.getcwd()

        print('MakeMoon ' + whichdir + '/In/big.in  ' + whichtime)

        # constants/variables
        big = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Moon', 'Saturn', 'Uranus', 'Neptune']
        bigxv = [''] * len(big)

        # Use chosen timestep
        timestep = int(whichtime)

        # Find the correct timestep for the planets
        # 0-8 without 5
        for i in [0, 1, 2, 3, 4, 6, 7, 8]:
            filename = f"{here}/{whichdir}/In/InitElemFiles/{big[i]}.aei"
			
            # Attempt to open the file; if it fails, move on
            try:
                with open(filename, 'r') as File:
                    for j in range(timestep):
                        thisline = File.readline().split()
                        bigxv[i] = thisline[6:]
            except FileNotFoundError:
                # File not found; skip this iteration and continue with the next
                continue

        # Moon parameters based on which run
        # B or D => smaller mass, H or L => larger (j)
        # 1 => smaller axis, 2 => larger axis
        # B or H  => small density, D or L => large density
        FakeFile = open('FakeMoons.txt', 'r')
        Fake = FakeFile.readlines()
        FakeFile.close()
        if whichdir[0] == 'B' or whichdir[0] == 'H':
            iFake = 1
        elif whichdir[0] == 'D' or whichdir[0] == 'L':
            iFake = 2
        iFake = 1
        if whichdir[0] == 'B' or whichdir[0] == 'D':
            jFake = 1
        elif whichdir[0] == 'H' or whichdir[0] == 'L':
            jFake = 2
        kFake = int(whichdir[-1])
        print([i, j])
        # assign large or small d, m, and a based on i, j, and k
        d = Fake[0].split()[iFake]
        m = str(float(Fake[1].split()[jFake]) / mSun)
        a = Fake[2].split()[kFake]

        # Generate Moon's position and velocity
        phi1 = 2 * pi * random()  # planar angle for position
        theta1 = 0.0  # polar angle for position (i=0 => 0)
        v = sqrt(G * 9.54266E-04 * mSun / float(a))  # orbital velocity = sqrt(GM/a)
        phi2 = phi1 + pi / 2  # planar angle for velocity
        theta2 = 0.0  # polar angle for velocity (i=0 => 0)

        x = float(a) * cos(phi1) * cos(theta1) / AU  # moon orbit relative to planet
        y = float(a) * sin(phi1) * cos(theta1) / AU
        z = float(a) * sin(theta1) / AU
        u = v * cos(phi2) * cos(theta2) * day / AU
        v = v * sin(phi2) * cos(theta2) * day / AU
        w = v * sin(theta2) * day / AU
        xvmod = [x, y, z, u, v, w]

        # Add Moon's position to Jupiter's
        bigxv[5] = [repr(float(bigxv[4][i]) + xvmod[i]) for i in range(6)]

        # Read density and mass of planets
        BigFirstData = MercModule.FILE_CONTENTS_PLANET_FIRST_LINES
        BigFirstData = [BigFirstData[i].split() for i, _ in enumerate(BigFirstData)]
        BigFirstData = numpy.array(BigFirstData)
        dpl = numpy.array([0.0 for _ in range(len(big))])
        mpl = numpy.array([0.0 for _ in range(len(big))])

        for j, _ in enumerate(big):
            if numpy.any(BigFirstData[:, 0] == big[j]):
                dpl[j] = BigFirstData[BigFirstData[:, 0] == big[j], 1][0]
                mpl[j] = BigFirstData[BigFirstData[:, 0] == big[j], 2][0]
        dpl[numpy.array(big) == 'Moon'] = d
        mpl[numpy.array(big) == 'Moon'] = m

        dpl = [str(dpl[i]) for i in range(len(dpl))]
        mpl = [str(mpl[i]) for i in range(len(dpl))]

        # Format data as the first line of each big.in object entry
        BigFirstLines = [big[i].ljust(10) + 'd= ' + dpl[i] + '  m= ' + mpl[i] + '\n'
                         for i in range(len(big))]

        # Read generic big.in file header
        BigHeader = MercModule.FILE_CONTENTS_BIG_HEADER

        # No spin for all objects
        bigs = ["  0.0  0.0  0.0\n"] * len(BigFirstLines)

        MercModule.WriteObjInFile(here, whichdir, big, 'big',
                                  BigHeader, BigFirstLines, bigxv, bigs)

        # Record which timestep was used
        timestepfile = open(here + '/' + whichdir + '/timestep.txt', 'w')
        timestepfile.write(repr(timestep))
        timestepfile.close()

    @staticmethod
    def MakeBigChoose(
        whichdir, 
        whichtime,
        big = ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Io', 'Europa', 'Ganymede', 'Callisto',
               'Saturn', 'Enceladu', 'Rhea', 'Titan', 'Iapetus', 'Uranus', 'Neptune']
):
        """
        Select a timestep for the big objects and make a new big.in
        """
        assert type(whichdir) is str
        assert type(whichtime) is str
        assert int(whichtime) >= 5

        here = os.getcwd()

        print('MakeBigChoose ' + whichdir + '/In/big.in  ' + whichtime)
        print(f"    {len(big)} big objects: {big}")

        # constants/variables
        bigxv = [''] * len(big)

        # Use chosen timestep
        timestep = int(whichtime)

        # Find the correct timestep for each big thing
        for i in range(len(big)):
            filename = here + '/' + whichdir + '/In/InitElemFiles/' + big[i] + '.aei'
            File = open(filename, 'r')
            for j in range(timestep):
                thisline = File.readline().split()
            bigxv[i] = thisline[6:]

        # Read density and mass of planets
        BigFirstData = MercModule.FILE_CONTENTS_PLANET_FIRST_LINES
        BigFirstData = [BigFirstData[i].split() for i in range(len(BigFirstData))]
        BigFirstData = numpy.array(BigFirstData)
        dpl = numpy.array([0.0 for _ in range(len(big))])
        mpl = numpy.array([0.0 for _ in range(len(big))])

        for j in range(len(big)):
            if numpy.any(BigFirstData[:, 0] == big[j]):
                dpl[j] = BigFirstData[BigFirstData[:, 0] == big[j], 1][0]
                mpl[j] = BigFirstData[BigFirstData[:, 0] == big[j], 2][0]

        dpl = [str(dpl[i]) for i in range(len(dpl))]
        mpl = [str(mpl[i]) for i in range(len(dpl))]

        # Format data as the first line of each big.in object entry
        BigFirstLines = [big[i].ljust(10) + 'd= ' + dpl[i] + '  m= ' + mpl[i] + '\n'
                         for i in range(len(big))]

        # Read generic big.in file header
        BigHeader = MercModule.FILE_CONTENTS_BIG_HEADER

        # No spin for all objects
        bigs = ["  0.0  0.0  0.0\n"] * len(BigFirstLines)

        MercModule.WriteObjInFile(here, whichdir, big, 'big',
                                  BigHeader, BigFirstLines, bigxv, bigs)

        # Record timestep used
        timestepfile = open(here + '/' + whichdir + '/timestep.txt', 'w')
        timestepfile.write(repr(timestep))
        timestepfile.close()

    @staticmethod
    def MakeBigRand(
            whichdir, 
            whichtime,
            big=['Mercury','Venus','Earth','Mars','Jupiter','Io','Europa','Ganymede','Callisto',
             'Saturn','Enceladu','Rhea','Titan','Iapetus','Uranus','Neptune'],
            seed=None,
        ):
        """
        Pick a random timestep for the big objects and make a new big.in
        """
        assert type(whichdir) is str
        assert type(whichtime) is str

        here=os.getcwd()

        print('MakeBigRand '+whichdir+'/In/big.in  '+whichtime)

        #constants/variables
        #	big=['Mercury','Venus','Earth','Mars','Jupiter',
        #	'Io','Europa','Ganymede','Callisto','Saturn','Uranus','Neptune']
        bigxv = [''] * len(big)

        ### Pick a timestep and get all big vectors at that point
        AEILen=MercModule.FileLength(here+'/'+whichdir+'/In/InitElemFiles/Jupiter.aei')-5
        if seed:
            timestep = 5 + seed
            assert seed <= AEILen - 5, f"Seed value '{seed}' exceeds maximum allowed value {AEILen-5}"
        else:
            timestep=5+int(AEILen*random())

        # Find the correct timestep for each big thing
        for i in range(len(big)):
            filename=here+'/'+whichdir+'/In/InitElemFiles/'+big[i]+'.aei'
            File=open(filename,'r')
            for j in range(timestep):
                thisline=File.readline().split()
            bigxv[i]=thisline[6:]

        ### Read density and mass of planets
        BigFirstData = MercModule.FILE_CONTENTS_PLANET_FIRST_LINES

        BigFirstData=[BigFirstData[i].split() for i in range(len(BigFirstData))]
        BigFirstData=numpy.array(BigFirstData)
        dpl=numpy.array([0.0 for _ in range(len(big))])
        mpl=numpy.array([0.0 for _ in range(len(big))])

        for j in range(len(big)):
            if numpy.any(BigFirstData[:,0]==big[j]):
                dpl[j]=BigFirstData[BigFirstData[:,0]==big[j],1][0]
                mpl[j]=BigFirstData[BigFirstData[:,0]==big[j],2][0]

        dpl=[str(dpl[i]) for i in range(len(dpl))]
        mpl=[str(mpl[i]) for i in range(len(dpl))]

        ### Format data as the first line of each big.in object entry
        BigFirstLines=[big[i].ljust(10)+'d= '+dpl[i]+'  m= '+mpl[i]+'\n'
                       for i in range(len(big))]

        ### Read generic big.in file header
        BigHeader = MercModule.FILE_CONTENTS_BIG_HEADER

        ### No spin for all objects
        bigs = ["  0.0  0.0  0.0\n"] * len(BigFirstLines)

        ### Write data
        MercModule.WriteObjInFile(here,whichdir,big,'big',
                                  BigHeader,BigFirstLines,bigxv,bigs)

        ### Record timestep used
        timestepfile=open(here+'/'+whichdir+'/timestep.txt','w')
        timestepfile.write(repr(timestep))
        timestepfile.close()

    @staticmethod
    def MakeSmall(whichdir,whichtime,n,whichpl,da,dv):
        """Make a random cluster of small objects around preselected ones to write to small.in."""
        assert type(whichdir) is str
        assert type(whichtime) is str
        assert type(n) is int
        assert n>=0

        here=os.getcwd()

        print('MakeSmall '+whichdir+'/In/small.in  '+whichtime+'  '+str(n))

        ### Constants/variables
        maxaspread=da/AU				#in AU
        maxvspread=dv*day/AU			#in AU/day

        small=['M'+str(i) for i in range(n)]
        smallxv=[''] * n

        ### Generate slightly randomized rocks at different phases of Jupiter or Saturn's orbit
        for j in range(len(small)):
            ### Pick a random timestep
            if whichpl=='J':
                filename=here+'/'+whichdir+'/In/InitElemFiles/Jupiter12Yr.aei'
            if whichpl=='S':
                filename=here+'/'+whichdir+'/In/InitElemFiles/Saturn29Yr.aei'
            AEILen=MercModule.FileLength(filename)-5
            timestep=5+int(AEILen*random())
            ### Get Jupiter/Saturn's info at this point
            File=open(filename,'r')
            for _ in range(timestep):
                thisline=File.readline().split()
            bigxv=thisline[6:]

            ### Generate random variation
            phi1=2*pi*random()
            theta1=-pi/2+pi*random()
            r=maxaspread*random()
            v=maxvspread*random()
            phi2=2*pi*random()
            theta2=-pi/2+pi*random()

            x=r*cos(phi1)*cos(theta1)
            y=r*sin(phi1)*cos(theta1)
            z=r*sin(theta1)
            u=v*cos(phi2)*cos(theta2)
            v=v*sin(phi2)*cos(theta2)
            w=v*sin(theta2)

            ### Coords = Jupiter/Saturn coords plus random variation
            smallxv[j]=[float(bigxv[0])+x, float(bigxv[1])+y, float(bigxv[2])+z,
                        float(bigxv[3])+u, float(bigxv[4])+v, float(bigxv[5])+w]
            smallxv[j]=[repr(i) for i in smallxv[j]]

        ### Read density and mass of planetesimals
        SmallFirstData = MercModule.FILE_CONTENTS_PLANET_FIRST_LINES

        SmallFirstData=[SmallFirstData[i].split()
                        for i in range(len(SmallFirstData))]
        SmallFirstData=numpy.array(SmallFirstData)
        d=str(SmallFirstData[SmallFirstData[:,0]=='Plantsml',1][0])
        m=str(SmallFirstData[SmallFirstData[:,0]=='Plantsml',2][0])

        ### Format data as the first line of each big.in object entry
        SmallFirstLines=[small[i].ljust(10)+'d= '+d+'  m= '+m+'  r= 0.001\n'
                         for i in range(len(small))]

        ### Read generic big.in file header
        SmallHeader = MercModule.FILE_CONTENTS_SMALL_HEADER

        ### No spin for all objects
        smalls=["  0.0  0.0  0.0\n"] * len(small)

        ### Write data
        MercModule.WriteObjInFile(current_dir=here,
                                  subdirectory=whichdir,
                                  names=small,
                                  filename='small',
                                  Header=SmallHeader,
                                  FirstLines=SmallFirstLines,
                                  xv=smallxv,
                                  s=smalls)

    @staticmethod
    def Good2Small(whichdir,whichtime,n):
        """Copy the small rocks from good.in to small.in"""
        assert type(whichdir) is str
        assert type(whichtime) is str
        assert type(n) is int
        assert n>=0

        here=os.getcwd()
        print('Good2Small '+whichdir+'/good.in  '+whichtime)

        ### Read in objects from good.in file
        #	goodin=open(whichdir+'/good.in','r')
        #	GoodLen=MercModule.FileLength(whichdir+'/good.in')
        goodin=open('good.in','r')
        GoodLen=MercModule.FileLength('good.in')
        if (GoodLen%4 != 0):
            print('??? good.in length = '+str(GoodLen))
        ngood=GoodLen/4
        ### If asked for more objects than available, give all and print warning
        if ngood < n:
            print('Warning: requested '+str(n)+' small objects. '+
                  'There are only '+str(ngood)+' good objects to use.')
            n=ngood
        ### New objects will be a random subset of the good list
        GoodInd=sample(
            list(range(ngood)),n
        )
        ### Create and fill vectors with the data from good.in
        header, pos, vel, s = [],[],[],[]
        for _ in range(ngood):
            header.append(goodin.readline())		# not used
            pos.append(goodin.readline().split())
            vel.append(goodin.readline().split())
            s.append(goodin.readline())

        ### Generate new, sequential names for the objects
        name=['M'+str(i) for i in range(n)]
        smallxv=[''] * len(n)
        smalls =[''] * len(n)

        ### Fill data of object j in new list with ind[j] from old list
        for j in range(n):
            smallxv[j]=pos[GoodInd[j]]+vel[GoodInd[j]]
            smalls[j] =s[GoodInd[j]]

        ### Read density and mass of planetesimals
        SmallFirstData = MercModule.FILE_CONTENTS_PLANET_FIRST_LINES

        SmallFirstData=[SmallFirstData[i].split()
                        for i in range(len(SmallFirstData))]
        SmallFirstData=numpy.array(SmallFirstData)
        d=str(SmallFirstData[SmallFirstData[:,0]=='Plantsml',1][0])
        m=str(SmallFirstData[SmallFirstData[:,0]=='Plantsml',2][0])

        ### Format data as the first line of each big.in object entry
        SmallFirstLines=[name[i].ljust(10)+'d= '+d+'  m= '+m+'  r= 0.001\n'
                         for i in range(len(name))]

        ### Read generic big.in file header
        SmallHeader = MercModule.FILE_CONTENTS_SMALL_HEADER

        ### Write data
        MercModule.WriteObjInFile(here,whichdir,name,'small',
                                  SmallHeader,SmallFirstLines,smallxv,smalls)


    @staticmethod
    def MakeSmallEjecta(
        whichdir,
        whichtime,
        n=1500,
        whichpl="Earth",
        fmin = 3.,
        fmax = 8.6978026,
    ):
        """ Construct and save a small.in file with n objects ejected from around the specified planet"""
        here=os.getcwd()
        print('MakeSmallEjecta ' + whichdir + '/small.in  ' + whichtime)

        ### Get physical parameters for the central planet
        ### Look up fron big.in (need to generate that first!)
        big_fname = here + '/' + whichdir + '/In/big.in'
        pl_info = []
        with open(big_fname, "r") as file:
            for line in file:
                if whichpl.lower() in line.lower():
                    pl_info.append(line)
                    for i in range(4):
                        pl_info.append(file.readline())
                    break

        ### Get the mass and density from the first line of the planet's input
        planet_first_line = [x for x in pl_info[0].split('  ')]
        Mplanet = float([x.strip() for x in planet_first_line if ("m=" in x)][0].replace("m=", "")) * mSun
        Dplanet = float([x.strip() for x in planet_first_line if ("d=" in x)][0].replace("d=", ""))
        ### Compute the radius using volume of a sphere
        Rplanet = ((3/(4*pi))*(Mplanet/Dplanet))**(1/3)

        ### Get position and velocity vectors from the next lines
        planetpos = [float(x) for x in pl_info[1].split()]
        planetvel = [float(x) for x in pl_info[2].split()]

        ### system parameters
        Mtot = 1.0e-8*Mplanet/mSun  # standard mass lost in collision
        m = Mtot/n  # mass per meteoroid

        Rhill=1.*(Mplanet/mSun)**(1./3.)  # in AU
        vesc=sqrt(2*G*Mplanet/(1.1*Rhill*AU + Rplanet))*day/AU  # in AU/day

        ### Assign random values for theta and phi
        theta = numpy.random.rand(n) * 360.
        phi = numpy.random.rand(n) * 180.

        ### Calculate position vectors based on these angles
        x = 1.1 * Rhill * numpy.cos(theta) * numpy.cos(phi)
        y = 1.1 * Rhill * numpy.sin(theta) * numpy.cos(phi)
        z = 1.1 * Rhill * numpy.sin(phi)
        pos = [[str(x[i] + planetpos[0]),
                str(y[i] + planetpos[1]),
                str(z[i] + planetpos[2])] for i in range(n)]

        ### Fraction of escape velocity for each ejected rock, randomized within specified range
        frac = fmin + random()*(fmax - fmin)
        ### Calculate velocity vectors
        u = frac * vesc * numpy.cos(theta) * numpy.cos(phi)
        v = frac * vesc * numpy.sin(theta) * numpy.cos(phi)
        w = frac * vesc * numpy.sin(phi)
        vel = [[str(u[i] + planetvel[0]),
                str(v[i] + planetvel[1]),
                str(w[i] + planetvel[2])] for i in range(n)]

        ### Name the objects numerically
        n_digits = len(str(n-1))
        name = [('M{:0>'+str(n_digits)+'}').format(str(i)) for i in range(n)]

        ### Assemble position and velocity vectors into needed shape
        small_xv = [pos[i] + vel[i] for i in range(n)]
        ### no spin
        small_s = ["  0.0  0.0  0.0\n"] * n

        ### Format data as the first line of each big.in object entry
        SmallFirstLines = [f'{name[i]}  m={m}  r=0.001 d=2.0\n'
                           for i in range(len(name))]

        ### Read generic big.in file header
        SmallHeader = MercModule.FILE_CONTENTS_SMALL_HEADER

        ### Write data
        MercModule.WriteObjInFile(here, whichdir, name, 'small',
                                  SmallHeader, SmallFirstLines, small_xv, small_s) 
