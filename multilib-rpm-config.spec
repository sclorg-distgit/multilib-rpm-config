%{?scl:%scl_package multilib-rpm-config}
%{!?scl:%global pkg_name %{name}}

# While we are in package playing with packaging principles, why about having
# this solved in redhat-rpm-config too?  (Also for RHELs which are alive, or
# EPELs otherwise).

# https://fedoraproject.org/wiki/Packaging:Guidelines#Packaging_of_Additional_RPM_Macros
%global macrosdir       %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{?scl:%{_root_sysconfdir}}%{!?scl:%{_sysconfdir}}/rpm; echo $d)

%global rrcdir          %_libexecdir

Summary: Multilib packaging helpers
Name: %{?scl_prefix}multilib-rpm-config
Version: 1
Release: 10%{?dist}
License: GPLv2+
URL: https://fedoraproject.org/wiki/PackagingDrafts/MultilibTricks

BuildRequires: gcc

Source0: multilib-fix
Source1: macros.ml
Source2: README
Source3: COPYING
Source4: multilib-library
Source5: multilib-info

BuildArch: noarch

# Most probably we want to move everything here?
Requires: redhat-rpm-config

%{!?_licensedir:%global license %doc}

%description
Set of tools (shell scripts, RPM macro files) to help with multilib packaging
issues.

%prep
%setup -n %{pkg_name}-%{version} -c -T
install -m 644 %{SOURCE2} %{SOURCE3} .

%build
%global ml_fix %rrcdir/multilib-fix
%global ml_info %rrcdir/multilib-info

lib_sed_pattern='/@LIB@/ {
    r %{SOURCE4}
    d
}'

sed -e 's|@ML_FIX@|%ml_fix|g' \
    -e 's|@ML_INFO@|%ml_info|g' \
    %{SOURCE1} > macros.multilib
sed -e "$lib_sed_pattern" \
    %{SOURCE0} > multilib-fix
sed -e "$lib_sed_pattern" \
    %{SOURCE5} > multilib-info

%install
mkdir -p %{buildroot}%{rrcdir}
mkdir -p %{buildroot}%{macrosdir}
# let the macros.multilib file implicitly conflict with non-SCL file, since we
# cannot install two packages that would define the same RPM macros
install -m 644 -p macros.multilib %{buildroot}/%{macrosdir}
install -m 755 -p multilib-fix %{buildroot}/%{ml_fix}
install -m 755 -p multilib-info %{buildroot}/%{ml_info}

%check
mkdir tests ; cd tests
ml_fix="sh `pwd`/../multilib-fix --buildroot `pwd`"
capable="sh `pwd`/../multilib-info --multilib-capable"

mkdir template
cat > template/main.c <<EOF
#include "header.h"
int main () { call (); return 0; }
EOF
cat > template/header.h <<EOF
#include <stdio.h>
void call (void) { printf ("works!\n"); }
EOF

cp -r template basic
gcc ./basic/main.c
./a.out

pwd
if `$capable`; then
    cp -r template really-works
    $ml_fix --file /really-works/header.h
    gcc really-works/main.c
    ./a.out
    test -f really-works/header-*.h
fi

cp -r template other_arch
$ml_fix --file /other_arch/header.h --arch ppc64
test -f other_arch/header-*.h

cp -r template other_arch_fix
$ml_fix --file /other_arch_fix/header.h --arch ppc64p7
test -f other_arch_fix/header-ppc64.h

cp -r template aarch64-no-change
$ml_fix --file /aarch64-no-change/header.h --arch aarch64
test ! -f aarch64-no-change/header-*.h

test `$capable --arch x86_64` = true
test `$capable --arch aarch64` = false
test `$capable --arch ppc64p7` = true

%files
%license COPYING
%doc README
%{rrcdir}/*
%{macrosdir}/*

%changelog
* Fri Jul 15 2016 Honza Horak <hhorak@redhat.com> - 1-10
- Fix rpm macros path specification

* Fri Jul 15 2016 Honza Horak <hhorak@redhat.com> - 1-9
- Use non-prefixed path for RPM macros

* Fri Jul 15 2016 Honza Horak <hhorak@redhat.com> - 1-8
- Move license macro definition after License tag

* Fri Jul 15 2016 Honza Horak <hhorak@redhat.com> - 1-7
- Convert to SCL package

* Fri Jul 01 2016 Yaakov Selkowitz <yselkowi@redhat.com> - 1-6
- Fix testsuite on non-multilib arches (#1352164)

* Wed Jun 22 2016 Pavel Raiskup <praiskup@redhat.com> - 1-5
- document why there is no need for '#else' in the replacement header
- add basic testsuite

* Mon Jun 13 2016 Pavel Raiskup <praiskup@redhat.com> - 1-4
- use '-' as a field separator by default

* Thu Jun 09 2016 Pavel Raiskup <praiskup@redhat.com> - 1-3
- package separately from redhat-rpm-config

* Fri Nov 27 2015 Pavel Raiskup <praiskup@redhat.com> - 1-2
- fix licensing in Sources
- allow undefined %%namespace

* Wed Nov 18 2015 Pavel Raiskup <praiskup@redhat.com> - 1-1
- initial packaging
