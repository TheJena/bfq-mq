Disclaimer
============
This repository is an experimental fork of BFQ for blk-mq;
it contains unstable and untested code. Please refer to
[BFQ-MQ](https://github.com/Algodev-github/bfq-mq) for
more stable improvements of the BFQ I/O scheduler.


Linux kernel
============

There are several guides for kernel developers and users. These guides can
be rendered in a number of formats, like HTML and PDF. Please read
[Documentation/admin-guide/README.rst](https://github.com/TheJena/bfq-mq-dev/blob/bfq-mq-dev/Documentation/admin-guide/README.rst)
first.

In order to build the documentation, use ``make htmldocs`` or
``make pdfdocs``.  The formatted documentation can also be read online at:
[https://www.kernel.org/doc/html/latest/](https://www.kernel.org/doc/html/latest/)

There are various text files in the
[Documentation/](https://github.com/TheJena/bfq-mq-dev/tree/bfq-mq-dev/Documentation)
subdirectory, several of them using the Restructured Text markup notation.  See
[Documentation/00-INDEX](https://github.com/TheJena/bfq-mq-dev/blob/bfq-mq-dev/Documentation/00-INDEX)
for a list of what is contained in each file.

Please read the
[Documentation/process/changes.rst](https://github.com/TheJena/bfq-mq-dev/blob/bfq-mq-dev/Documentation/process/changes.rst)
file, as it contains the requirements for building and running the kernel, and
information about the problems which may result by upgrading your kernel.
